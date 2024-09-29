# import matplotlib.pyplot as plt
import numpy as np
from imgui_bundle import hello_imgui, imgui
from scipy.spatial import KDTree
from fireflies.basic import Firefly
# from fireflies.broken import Firefly

def xy_random_normal(count: int, sigma_x: float, sigma_y: float, seed: int):
    rng = np.random.default_rng(seed)
    xy = rng.normal((0.0, 0.0), (sigma_x, sigma_y), (count, 2))
    return xy[:, 0], xy[:, 1]


def xy_random_uniform(count: int, low: tuple[int, int], high: tuple[int, int]):
    rng = np.random.default_rng(42)
    xy = rng.uniform(low, high, (count, 2))
    return xy[:, 0], xy[:, 1]


def test_xy_random_normal():
    for i in range(25):
        sigma_x, sigma_y = np.random.uniform(1, 50, 2)
        count = (i + 1) * 10000
        x, y = xy_random_normal(count, sigma_x, sigma_y)
        np.testing.assert_allclose(np.mean(x), [0.0], atol=1e-1 * sigma_x)
        np.testing.assert_allclose(np.mean(y), [0.0], atol=1e-1 * sigma_y)
        np.testing.assert_allclose(np.std(x), sigma_x, atol=1e-1 * sigma_x)
        np.testing.assert_allclose(np.std(y), sigma_y, atol=1e-1 * sigma_y)


def test_xy_random_uniform():
    for i in range(25):
        count = (i + 1) * 10000
        low_x, high_x = np.random.uniform(1, 50, 2)
        if high_x < low_x:
            low_x, high_x = high_x, low_x
        low_y, high_y = np.random.uniform(1, 50, 2)
        if high_y < low_y:
            low_y, high_y = high_y, low_y

        x, y = xy_random_uniform(count, (low_x, low_y), (high_x, high_y))
        np.testing.assert_allclose(np.mean(x), (low_x + high_x) / 2, atol=0.5)
        np.testing.assert_allclose(np.mean(y), (low_y + high_y) / 2, atol=0.5)
        np.testing.assert_allclose(np.max(x), high_x, atol=0.05)
        np.testing.assert_allclose(np.min(x), low_x, atol=0.05)
        np.testing.assert_allclose(np.max(y), high_y, atol=0.05)
        np.testing.assert_allclose(np.min(y), low_y, atol=0.05)


def draw_fireflies(x, y, fireflies):
    draw_list = imgui.get_window_draw_list()
    window_size = imgui.get_window_size()
    cursor = imgui.get_cursor_screen_pos()
    for x, y, firefly in zip(x, y, fireflies):
        # transform_mat = self.image_params.zoom_pan_matrix
        draw_list.add_circle_filled(
            imgui.ImVec2(
                cursor.x + x + window_size.x / 2, cursor.y + y + window_size.y / 2
            ),
            10,
            0xff0000FF | (int(firefly.brightness) << 24) | (int(firefly.brightness) << 8),
        )

class FirefliesVisualizer:
    def __init__(self):
        self.canvas = np.zeros((1024, 1024))
        self.count = 30
        self.x = None
        self.y = None
        self.sigma_x = 100
        self.sigma_y = 100
        self.mean_speed = 0.1
        self.t = 0
        self.neighbour_tree = None
        self.data = None
        self.dampening = 0.9
        self.radius = 50
        self.seed = 42
        self.fireflies = None
        self.preferred_duration = 300
        self.preferred_duration_sigma = 0
        self.initial_phase_sigma = 20
        self.events = None
        self.speed = 1
        self.transmission_time = 0
        self.transmission_time_sigma = 0
        self.transmission_error_rate = 0
        self.transmission_rng = None

    def frame(self):
        if(hello_imgui.get_runner_params().app_shall_exit == True):
            return
        imgui.set_next_window_pos(imgui.ImVec2(0.0, 20.0))
        w, h = imgui.get_io().display_size
        imgui.set_next_window_size(imgui.ImVec2(w*0.66, h*0.9))
        imgui.begin("Fireflies")
        if not self.x is None and not self.y is None:
            # self.c = (128 + 128*np.cos(self.freq*self.t + self.phase)).astype(np.uint8)
            for i, (x, y) in enumerate(zip(self.x, self.y)):
                # if np.random.random() > 0.5:
                #     continue
                # neighbours = self.neighbour_tree.query_ball_point((x, y), self.radius, 2)
                self.fireflies[i].tick(self.speed)
                unprocessed_events = []
                for event in self.events[i]:
                    if event[0] > self.t:
                        unprocessed_events.append(event)
                        continue
                    self.fireflies[i].receive_pulse(event[1])
                self.events[i] = unprocessed_events
                # self.phase[i] = self.phase[i]*self.phase_dampening + self.phase_step*np.mean(self.phase[neighbours])
                # self.freq[i] = self.freq[i]*self.freq_dampening + self.freq_step*np.mean(self.freq[neighbours])
            draw_fireflies(self.x, self.y, self.fireflies)
            draw_list = imgui.get_window_draw_list()
            window_size = imgui.get_window_size()
            cursor = imgui.get_cursor_screen_pos()
            draw_list.add_circle(
                imgui.ImVec2(
                    cursor.x + window_size.x / 2, cursor.y + window_size.y / 2
                ),
                self.radius,
                0x000000FF | (255 << 24))
            
        imgui.end()
        imgui.set_next_window_pos(imgui.ImVec2(w*0.66, 0))
        imgui.set_window_size(imgui.ImVec2(0.33*w, 0.9*h))
        imgui.begin("Settings")
        imgui.collapsing_header("Setup")
        count_changed, self.count = imgui.slider_int("Count", self.count, 1, 400)
        sigma_x_changed, self.sigma_x = imgui.slider_int("Sigma X", self.sigma_x, 1, 500)
        sigma_y_changed, self.sigma_y = imgui.slider_int("Sigma Y", self.sigma_y, 1, 500)
        seed_changed, self.seed = imgui.slider_int("Random Seed", self.seed, 1, 1024)
        initial_phase_sigma_changed, self.initial_phase_sigma = imgui.slider_int("Initial Shift Sigma", self.initial_phase_sigma, 0, 100)
        # imgui.end()
        imgui.collapsing_header("Adjustments")
        dampening_changed, self.dampening = imgui.slider_float("Dampening power", self.dampening, 0, 1)
        preferred_duration_changed, self.preferred_duration = imgui.slider_int("Preferred Duration", self.preferred_duration, 1, 10000)
        preferred_duration_sigma_changed, self.preferred_duration_sigma = imgui.slider_int("Preferred Duration Sigma", self.preferred_duration_sigma, 0, 100)
        radius_changed, self.radius = imgui.slider_float("Radius", self.radius, 1, 500)

        imgui.collapsing_header("Simulation Adjustments")
        speed_changed, self.speed = imgui.slider_float("Simulation speed", self.speed, 0, 10.0)
        transmission_time_changed, self.transmission_time = imgui.slider_int("Transmission Time", self.transmission_time, 0, 500)
        transmission_time_sigma_changed, self.transmission_time_sigma = imgui.slider_int("Transmission Time Sigma", self.transmission_time_sigma, 0, 100)
        transmission_error_rate_changed, self.transmission_error_rate = imgui.slider_float("Transmission Error Rate", self.transmission_error_rate, 0.0, 1.0)
        imgui.end()
        self.t += self.speed
        # After changing one of these properties we need to reset the simulation
        resetup = any([count_changed, sigma_x_changed, sigma_y_changed, seed_changed, initial_phase_sigma_changed]) or (self.events is None)
        # After one of these changes, we can just adjust the simulation
        readjust = any([resetup, dampening_changed, radius_changed, preferred_duration_changed, preferred_duration_sigma_changed, speed_changed, transmission_time_changed, transmission_time_sigma_changed, transmission_error_rate_changed])
        if resetup:
            self.x, self.y = xy_random_normal(self.count, self.sigma_x, self.sigma_y, self.seed)
            self.data = np.stack((self.x, self.y), axis=1)
            self.neighbour_tree = KDTree(data=self.data, leafsize=25)
            self.fireflies = np.empty( (self.count), dtype=object)
            self.events = np.empty( (self.count), dtype=object)
            rng = np.random.default_rng(self.seed)
            duration_rng = np.random.default_rng(self.seed)
            self.transmission_rng = np.random.default_rng(self.seed)
            for i in range(self.count):
                self.events[i] = []
                duration = duration_rng.uniform(self.preferred_duration-self.preferred_duration_sigma, self.preferred_duration+self.preferred_duration_sigma, (1))[0]
                shift = rng.uniform(0, duration * (self.initial_phase_sigma/100), (1))[0]
                new_firefly = Firefly()
                new_firefly.name = str(i)
                new_firefly.pulse_progress = shift
                self.fireflies[i]=new_firefly
        if readjust:
            rng = np.random.default_rng(self.seed)
            duration_rng = np.random.default_rng(self.seed)
            for i in range(self.count):
                def send_pulse(pulse):
                    neighbours = self.neighbour_tree.query_ball_point((self.x[i], self.y[i]), self.radius, 2)
                    for events in self.events[neighbours]:
                        success_roll = self.transmission_rng.uniform(0.0,1.0, (1))[0]
                        if success_roll < self.transmission_error_rate:
                            # Transmission failed
                            continue
                        min_transmission_time = max(self.transmission_time - self.transmission_time_sigma, 0)
                        max_transmission_time = self.transmission_time + self.transmission_time_sigma
                        delay = self.transmission_rng.uniform(min_transmission_time,max_transmission_time, (1))[0]
                        transmission_timestamp = self.t + delay
                        
                        events.append((transmission_timestamp, pulse))

                duration = duration_rng.uniform(self.preferred_duration-self.preferred_duration_sigma, self.preferred_duration+self.preferred_duration_sigma, (1))[0]
                firefly = self.fireflies[i]
                firefly.name = str(i)
                firefly.preferred_pulse_length = duration
                firefly.send_pulse = send_pulse
                firefly.dampening = self.dampening


def status():
    imgui.text("Status Bar")
if __name__ == "__main__":
    fireflies_visualizer = FirefliesVisualizer()
    callbacks = hello_imgui.RunnerCallbacks(fireflies_visualizer.frame, show_status=status)
    fps_idling = hello_imgui.FpsIdling(200, enable_idling=False)
    appwindow_params = hello_imgui.AppWindowParams("Fireflies")
    imgui_window_params = hello_imgui.ImGuiWindowParams(show_menu_bar=True, show_status_bar=True)
    runner_params = hello_imgui.RunnerParams(callbacks, appwindow_params,imgui_window_params, fps_idling=fps_idling)
    hello_imgui.run(runner_params)
