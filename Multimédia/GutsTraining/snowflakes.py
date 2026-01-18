import pygame
import random
import math
import lib


class Snowflake:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.speed = random.uniform(10, 27)
        self.drift = random.uniform(-20, 20)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-90, 90)
        self.size = random.randint(2, 6)
        self.opacity = random.uniform(0.6, 1.0)
        
        self.swing_amplitude = random.uniform(10, 30)
        self.swing_frequency = random.uniform(0.5, 2.0)
        self.swing_offset = random.uniform(0, math.pi * 2)
        
        self.flake_type = 0
        self.lifetime = 0.0
        
    def update(self, dt):
        self.lifetime += dt
        
        self.y += self.speed * dt
        
        swing = math.sin(self.lifetime * self.swing_frequency + self.swing_offset) * self.swing_amplitude
        self.x += (self.drift + swing) * dt
        
        self.rotation += self.rotation_speed * dt
        
        if self.y > self.height + 10:
            self.y = -10
            self.x = random.uniform(0, self.width)
            self.lifetime = 0.0
        
        if self.x < -10:
            self.x = self.width + 10
        elif self.x > self.width + 10:
            self.x = -10
    
    def draw(self, surface):
        flake_size = self.size * 6
        flake_surface = pygame.Surface((flake_size, flake_size), pygame.SRCALPHA)
        
        center = flake_size // 2
        
        if self.flake_type == 0:
            self._draw_star_flake(flake_surface, center, self.size)
        elif self.flake_type == 1:
            self._draw_dendritic_flake(flake_surface, center, self.size)
        elif self.flake_type == 2:
            self._draw_cross_flake(flake_surface, center, self.size)
        else:
            self._draw_hex_flake(flake_surface, center, self.size)
        
        rotated = pygame.transform.rotate(flake_surface, self.rotation)
        rotated.set_alpha(int(255 * self.opacity))
        
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated, rect)
    
    def _draw_star_flake(self, surface, center, size):
        num_branches = 6
        
        for i in range(num_branches):
            angle = i * (360 / num_branches)
            rad = math.radians(angle)
            
            end_x = center + int(math.cos(rad) * size * 3)
            end_y = center + int(math.sin(rad) * size * 3)
            
            steps = size * 2
            for step in range(steps):
                t = step / steps
                px = int(center + math.cos(rad) * size * 3 * t)
                py = int(center + math.sin(rad) * size * 3 * t)
                
                brightness = 1.0 - t * 0.3
                color = self._get_snow_color(px, py, brightness)
                
                if 0 <= px < surface.get_width() and 0 <= py < surface.get_height():
                    surface.set_at((px, py), color)
            
            for side in [-1, 1]:
                side_angle = angle + side * 30
                side_rad = math.radians(side_angle)
                branch_start = size * 1.5
                
                for step in range(int(size)):
                    t = step / size
                    px = int(center + math.cos(rad) * branch_start + math.cos(side_rad) * size * t)
                    py = int(center + math.sin(rad) * branch_start + math.sin(side_rad) * size * t)
                    
                    color = self._get_snow_color(px, py, 0.9)
                    if 0 <= px < surface.get_width() and 0 <= py < surface.get_height():
                        surface.set_at((px, py), color)
    
    def _draw_dendritic_flake(self, surface, center, size):
        num_branches = 6
        
        for i in range(num_branches):
            angle = i * (360 / num_branches)
            rad = math.radians(angle)
            
            for step in range(size * 3):
                t = step / (size * 3)
                px = int(center + math.cos(rad) * step)
                py = int(center + math.sin(rad) * step)
                
                color = self._get_snow_color(px, py, 1.0 - t * 0.2)
                if 0 <= px < surface.get_width() and 0 <= py < surface.get_height():
                    surface.set_at((px, py), color)
                
                if step % (size // 2) == 0 and step > 0:
                    for side in [-1, 1]:
                        sub_angle = angle + side * 45
                        sub_rad = math.radians(sub_angle)
                        
                        for sub_step in range(size):
                            sub_px = int(px + math.cos(sub_rad) * sub_step)
                            sub_py = int(py + math.sin(sub_rad) * sub_step)
                            
                            color = self._get_snow_color(sub_px, sub_py, 0.85)
                            if 0 <= sub_px < surface.get_width() and 0 <= sub_py < surface.get_height():
                                surface.set_at((sub_px, sub_py), color)
    
    def _draw_cross_flake(self, surface, center, size):
        for angle in [0, 90, 180, 270]:
            rad = math.radians(angle)
            
            for step in range(size * 3):
                px = int(center + math.cos(rad) * step)
                py = int(center + math.sin(rad) * step)
                
                thickness = max(1, size // 3 - step // (size * 2))
                
                for dx in range(-thickness, thickness + 1):
                    for dy in range(-thickness, thickness + 1):
                        tx = px + dx
                        ty = py + dy
                        
                        if 0 <= tx < surface.get_width() and 0 <= ty < surface.get_height():
                            brightness = 1.0 - (abs(dx) + abs(dy)) / (thickness * 4)
                            color = self._get_snow_color(tx, ty, brightness)
                            surface.set_at((tx, ty), color)
    
    def _draw_hex_flake(self, surface, center, size):
        hex_points = []
        for i in range(6):
            angle = i * 60
            rad = math.radians(angle)
            px = center + int(math.cos(rad) * size * 2)
            py = center + int(math.sin(rad) * size * 2)
            hex_points.append((px, py))
        
        for y in range(surface.get_height()):
            for x in range(surface.get_width()):
                dx = x - center
                dy = y - center
                dist = math.sqrt(dx**2 + dy**2)
                
                if dist <= size * 2:
                    angle = math.atan2(dy, dx)
                    facet = int((angle + math.pi) / (math.pi / 3)) % 6
                    brightness = 0.8 + (facet % 2) * 0.2
                    
                    color = self._get_snow_color(x, y, brightness)
                    surface.set_at((x, y), color)
        
        pygame.draw.polygon(surface, lib.SNOW_COLORS[2], hex_points, 1)
    
    def _get_snow_color(self, x, y, brightness):
        brightness = max(0.0, min(1.0, brightness))
        
        if brightness > 0.85:
            target = lib.SNOW_COLORS[0]
        elif brightness > 0.6:
            target = lib.SNOW_COLORS[1]
        else:
            target = lib.SNOW_COLORS[2]
        
        return lib.dither_pixel(x, y, target, lib.SNOW_COLORS)


class SnowfallSystem:
    def __init__(self, width, height, num_flakes=80):
        self.width = width
        self.height = height
        self.flakes = []
        
        for i in range(num_flakes):
            x = random.uniform(0, width)
            y = random.uniform(-height, height)
            flake = Snowflake(x, y, width, height)
            self.flakes.append(flake)
    
    def update(self, dt):
        for flake in self.flakes:
            flake.update(dt)
    
    def draw(self, surface):
        for flake in self.flakes:
            flake.draw(surface)
