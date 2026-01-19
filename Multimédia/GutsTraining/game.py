

import pygame
from typing import List
import math
import random
import os
import lib
import snowflakes  


def show_palette_test(screen):
    """
    Affiche toutes les couleurs de la palette pour vérifier.
    Chaque couleur = carré 30×30 pixels.
    """
    x, y = 10, 100
    
    for i, color in enumerate(lib.FULL_PALETTE):
        pygame.draw.rect(screen, color, (x, y, 30, 30))
        
        pygame.draw.rect(screen, (0, 0, 0), (x, y, 30, 30), 1)
        
        font = pygame.font.Font(None, 16)
        num_text = font.render(str(i), True, (255, 255, 255))
        screen.blit(num_text, (x + 8, y + 8))
        
        x += 35
        if (i + 1) % 8 == 0:
            x = 10
            y += 35


def render_scene(scene: lib.Scene) -> bool:

    screen = scene.screen
    width, height = scene.window_size
    
    dt = scene.clock.get_time() / 1000.0
    if hasattr(scene, 'snowfall') and scene.snowfall is not None:
        scene.snowfall.update(dt)
    
    # ZONE 1+2 : CIEL + COLLINE (pré-calculés, juste un blit !)
    if scene.static_background is not None:
        screen.blit(scene.static_background, (0, 0))
    
    # ZONE 3 : SOLEIL (cercle de 80px de diamètre)
    sun_color = (255, 220, 100)  # Jaune soleil
    sun_pos = (width - 120, 80)  # En haut à droite
    pygame.draw.circle(screen, sun_color, sun_pos, 40)
    
    # ZONE 4 : PLAN MOYEN TEXTURÉ (terre/herbe/neige avec dithering)
    if hasattr(scene, 'middle_ground') and scene.middle_ground is not None:
        screen.blit(scene.middle_ground, (0, 280))
    
    # Petite maison TRÈS lointaine 
    house_x = width - 120
    house_y = 345
    
 
    house_wall_color = (70, 75, 85)
    pygame.draw.rect(screen, house_wall_color, (house_x, house_y, 20, 15))
    
    roof_color = (35, 35, 40)
    roof_points = [
        (house_x - 2, house_y),           
        (house_x + 10, house_y - 12),     
        (house_x + 22, house_y)           
    ]
    pygame.draw.polygon(screen, roof_color, roof_points)
    

    chimney_color = (50, 45, 45)
    pygame.draw.rect(screen, chimney_color, (house_x + 14, house_y - 8, 3, 5))
    
 
    smoke_color = (140, 145, 150)
    pygame.draw.circle(screen, smoke_color, (house_x + 16, house_y - 10), 1)
    pygame.draw.circle(screen, smoke_color, (house_x + 17, house_y - 13), 1)
    

    window_color = (220, 200, 120)
    pygame.draw.rect(screen, window_color, (house_x + 8, house_y + 5, 4, 5))
    

    door_color = (40, 35, 30)
    pygame.draw.rect(screen, door_color, (house_x + 3, house_y + 7, 4, 8))
    
    # ZONE 5 : ARBRE HIVERNAL 
    # Utilise des frames pré calculées pour l'animation
    if hasattr(scene, 'tree_animation') and scene.tree_animation is not None:
        
        wind_time = scene.time_game * 0.8
        frame_index = int((wind_time * 8) % len(scene.tree_animation))  # 8 frames/sec
        
        current_tree = scene.tree_animation[frame_index]
        screen.blit(current_tree, (10, 70))  
    
    
    # ZONE 7 : NEIGE AU SOL  Texture détaillée
    if hasattr(scene, 'snow_ground') and scene.snow_ground is not None:
        screen.blit(scene.snow_ground, (0, 420))
    
    # ZONE 8 : FLOCONS DE NEIGE (premier plan, animés)
    if hasattr(scene, 'snowfall') and scene.snowfall is not None:
        scene.snowfall.draw(screen)
    
    # TEST DE LA PALETTE : Affiche les couleurs
    #show_palette_test(screen) la palette disponible
    
   
    
    return True  


def create_static_background(scene: lib.Scene):

    width, height = scene.window_size
    import math
    
    print("Génération du background statique (ciel + colline)...")
    
    bg = pygame.Surface((width, 280))  
    
    # ZONE 1 : CIEL HIVERNAL (280px de haut)
    sky_top = lib.SKY_COLORS[5]      
    sky_bottom = lib.SKY_COLORS[0]   
    
    
    for y in range(280):
        for x in range(width):
            pixel_color = lib.dither_gradient(
                x, y,
                sky_top, sky_bottom,
                0, 280,
                lib.SKY_COLORS
            )
            bg.set_at((x, y), pixel_color)
    
    # ZONE 2 : MONTAGNES EN PLUSIEURS COUCHES , effet de profondeur
    
    
    
    mountains = [
        # Arrière-plan (lointain, clair, plus larges)
        (width * 0.2, 200, 100, 0),   
        (width * 0.7, 250, 120, 0),   
        
       
        (width * 0.45, 180, 140, 1),  
        (width * 0.85, 160, 110, 1),  
        
     
        (width * 0.15, 120, 160, 2),  
        (width * 0.6, 140, 150, 2),   
    ]
    
    mountain_base_y = 280  
    
    # Dessine chaque montagne de l'arrière vers l'avant
    for center_x, mtn_width, mtn_height, color_depth in mountains:
        for x in range(width):
            dx = (x - center_x) / (mtn_width / 2)
            
            if abs(dx) <= 1.0:  

                peak_y = mountain_base_y - mtn_height * (1 - abs(dx))
                

                for y in range(int(peak_y), mountain_base_y):
                    if 0 <= y < 280:  
                        if color_depth == 0:
                            top_color = lib.HILL_COLORS[0]
                            bottom_color = lib.HILL_COLORS[1]
                        elif color_depth == 1:
                            top_color = lib.HILL_COLORS[1]
                            bottom_color = lib.HILL_COLORS[2]
                        else:
                            top_color = lib.HILL_COLORS[2]
                            bottom_color = (100, 110, 125)  
                        
                        pixel_color = lib.dither_gradient(
                            x, y,
                            top_color,
                            bottom_color,
                            int(peak_y), mountain_base_y,
                            lib.HILL_COLORS
                        )
                        bg.set_at((x, y), pixel_color)
    
    print("Background statique généré !")
    return bg


def create_middle_ground(scene: lib.Scene):

    width = scene.window_size[0]
    import random
    import math
    
    print("Génération du plan moyen (perspective 3/4 + dégradé vert + patates de neige)...")
    
    mg_surface = pygame.Surface((width, 140))
    
   
    grass_far = lib.GRASS_COLORS[0]      
    grass_near = lib.GRASS_COLORS[3]     
    
    random.seed(42)
    
    for y in range(140):
        for x in range(width):
            depth = y / 140.0
            

            perspective_x = x + math.sin(y / 20.0) * (1.0 - depth) * 5
            
            random.seed(int(perspective_x) * 13 + y * 7)
            noise = (random.random() - 0.5) * 0.15
            
            t = depth + noise
            t = max(0.0, min(1.0, t))
            
            r = int(grass_far[0] + (grass_near[0] - grass_far[0]) * t)
            g = int(grass_far[1] + (grass_near[1] - grass_far[1]) * t)
            b = int(grass_far[2] + (grass_near[2] - grass_far[2]) * t)
            
            target = (r, g, b)
            
            # Applique le dithering
            pixel_color = lib.dither_pixel(x, y, target, lib.GRASS_COLORS)
            mg_surface.set_at((x, y), pixel_color)
    
    # 2. TACHES DE NEIGE 
    random.seed(789)
    num_snow_patches = 12  
    
    for patch_idx in range(num_snow_patches):
        patch_y = random.randint(0, 140)
        patch_x = random.randint(0, width)
        
        depth = patch_y / 140.0 
        size_min = int(15 + depth * 20)  
        size_max = int(30 + depth * 30)  
        patch_base_size = random.randint(size_min, size_max)
        
        vertical_scale = 0.6 + depth * 0.4 
        

        scan_size = patch_base_size + 20
        for dy in range(-scan_size, scan_size):
            for dx in range(-scan_size, scan_size):
                px = patch_x + dx
                py = patch_y + int(dy * vertical_scale)
                
                if 0 <= px < width and 0 <= py < 140:
                    if dx == 0 and dy == 0:
                        dist = 0
                    else:
                        angle = math.degrees(math.atan2(dy, dx)) % 360
                        dist = math.sqrt(dx**2 + (dy * vertical_scale)**2)

                        random.seed(patch_idx * 1000 + int(angle * 10))
                        radius_variation = random.uniform(0.6, 1.3)
                        
                        
                        wave1 = math.sin(math.radians(angle * 3)) * 0.25
                        wave2 = math.cos(math.radians(angle * 5)) * 0.15
                        
                     
                        effective_radius = patch_base_size * radius_variation * (1 + wave1 + wave2)
                        
                      
                        dist_normalized = dist / effective_radius
                        
                        
                        random.seed(px * 73 + py * 131)
                        edge_noise = random.uniform(-0.2, 0.2)
                        
                        
                        if dist_normalized + edge_noise < 1.0:
                            # Couleur de neige selon distance du centre
                            if dist_normalized < 0.3:
                                target = lib.SNOW_COLORS[0]  # Blanc pur (centre)
                            elif dist_normalized < 0.7:
                                target = lib.SNOW_COLORS[1]  # Blanc bleuté
                            else:
                                target = lib.SNOW_COLORS[2]  # Gris clair (bords)
                            
                            pixel_color = lib.dither_pixel(px, py, target, lib.SNOW_COLORS)
                            mg_surface.set_at((px, py), pixel_color)
    
    print("Plan moyen généré !")
    return mg_surface


def draw_sword(surface, x, base_y, height, angle_offset=0):
    blade_width = max(3, height // 15)
    handle_height = height // 4
    blade_height = height - handle_height
    guard_width = blade_width * 4
    
    angle_rad = math.radians(angle_offset)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    def rotate_point(px, py):
        rx = x + (px - x) * cos_a - (py - base_y) * sin_a
        ry = base_y + (px - x) * sin_a + (py - base_y) * cos_a
        return int(rx), int(ry)
    
    for y_offset in range(blade_height):
        py = base_y - handle_height - y_offset
        t = y_offset / blade_height
        current_width = int(blade_width * (0.3 + t * 0.7))
        
        for dx in range(-current_width, current_width + 1):
            px = x + dx
            rx, ry = rotate_point(px, py)
            
            if 0 <= rx < surface.get_width() and 0 <= ry < surface.get_height():
                center_groove = abs(dx) < max(1, current_width // 3)
                center_highlight = abs(dx) <= 1
                
                random.seed(rx * 17 + int(py / 3) * 31)
                scratch = random.random() > 0.92
                
                edge_factor = abs(dx) / max(1, current_width)
                vertical_factor = 1.0 - (y_offset / blade_height) * 0.2
                
                if center_highlight:
                    brightness = 0.95
                elif center_groove:
                    brightness = 0.4 + vertical_factor * 0.2
                elif scratch:
                    brightness = 0.3
                else:
                    brightness = (0.8 - edge_factor * 0.4) * vertical_factor
                
                brightness = max(0.0, min(1.0, brightness))
                
                if brightness > 0.85:
                    target = lib.GUTS_COLORS[2]
                elif brightness > 0.65:
                    target = lib.GUTS_COLORS[0]
                elif brightness > 0.45:
                    target = lib.GUTS_COLORS[1]
                else:
                    target = lib.GUTS_COLORS[3]
                
                pixel_color = lib.dither_pixel(rx, ry, target, lib.GUTS_COLORS[:4])
                surface.set_at((rx, ry), pixel_color)
    
    guard_y = base_y - handle_height
    guard_thickness = max(2, blade_width // 2)
    
    for dx in range(-guard_width, guard_width + 1):
        for dy in range(-guard_thickness, guard_thickness + 1):
            px = x + dx
            py = guard_y + dy
            rx, ry = rotate_point(px, py)
            
            if 0 <= rx < surface.get_width() and 0 <= ry < surface.get_height():
                dist_from_center = abs(dx)
                
                if dist_from_center > guard_width * 0.7:
                    brightness = 0.6
                else:
                    brightness = 0.4 + (1.0 - dist_from_center / guard_width) * 0.2
                
                if abs(dy) == guard_thickness:
                    brightness *= 0.7
                
                if brightness > 0.6:
                    target = lib.GUTS_COLORS[0]
                elif brightness > 0.4:
                    target = lib.GUTS_COLORS[1]
                else:
                    target = lib.GUTS_COLORS[3]
                
                pixel_color = lib.dither_pixel(rx, ry, target, lib.GUTS_COLORS[:4])
                surface.set_at((rx, ry), pixel_color)
    
    handle_width = max(2, blade_width - 1)
    
    for y_offset in range(handle_height):
        py = base_y - y_offset
        segment = (y_offset // 3) % 2
        
        for dx in range(-handle_width, handle_width + 1):
            px = x + dx
            rx, ry = rotate_point(px, py)
            
            if 0 <= rx < surface.get_width() and 0 <= ry < surface.get_height():
                if segment == 0:
                    target = lib.GUTS_COLORS[3]
                else:
                    target = lib.GUTS_COLORS[1]
                
                pixel_color = lib.dither_pixel(rx, ry, target, lib.GUTS_COLORS[:4])
                surface.set_at((rx, ry), pixel_color)
    
    pommel_y = base_y
    pommel_size = blade_width + 1
    
    for dx in range(-pommel_size, pommel_size + 1):
        for dy in range(-pommel_size, pommel_size + 1):
            px = x + dx
            py = pommel_y + dy
            rx, ry = rotate_point(px, py)
            
            if 0 <= rx < surface.get_width() and 0 <= ry < surface.get_height():
                dist = math.sqrt(dx**2 + dy**2)
                if dist <= pommel_size:
                    sphere_factor = 1.0 - (dist / pommel_size)
                    light_side = dx > 0
                    
                    if light_side and sphere_factor > 0.6:
                        target = lib.GUTS_COLORS[0]
                    else:
                        target = lib.GUTS_COLORS[1]
                    
                    pixel_color = lib.dither_pixel(rx, ry, target, lib.GUTS_COLORS[:4])
                    surface.set_at((rx, ry), pixel_color)


def create_snow_ground(scene: lib.Scene):
    width, height = scene.window_size
    import random
    
    print("Génération du sol enneigé avec texture...")
    
    snow_surface = pygame.Surface((width, 60))
    random.seed(42)
    
    for y in range(60):
        for x in range(width):
            base_brightness = 1.0 - (y / 60) * 0.3
            noise = (random.random() - 0.5) * 0.4
            import math
            wave_x = math.sin(x / 20.0) * 0.1
            wave_y = math.cos(y / 10.0) * 0.1
            brightness = base_brightness + noise + wave_x + wave_y
            brightness = max(0.0, min(1.0, brightness))
            if brightness > 0.8:
                target = lib.SNOW_COLORS[0]
            elif brightness > 0.5:
                target = lib.SNOW_COLORS[1]
            else:
                target = lib.SNOW_COLORS[2]
            pixel_color = lib.dither_pixel(x, y, target, lib.SNOW_COLORS)
            snow_surface.set_at((x, y), pixel_color)
    
    random.seed(999)
    num_swords = 12
    for sword_idx in range(num_swords):
        sword_x = random.randint(30, width - 30)
        depth_in_snow = random.randint(10, 25)
        sword_y = 60 - depth_in_snow
        sword_height = random.randint(35, 55)
        angle = random.randint(-20, 20)
        draw_sword(snow_surface, sword_x, sword_y, sword_height, angle)
    
    print("Sol enneigé avec épées généré !")
    return snow_surface


def draw_tree_branch(surface, x, y, angle, length, thickness, depth, max_depth, side_bias=0, wind_offset=0):
    if depth > max_depth or length < 2:
        return
    wind_strength = (depth / max_depth) * wind_offset
    angle += wind_strength
    rad = math.radians(angle)
    end_x = x + length * math.cos(rad)
    end_y = y - length * math.sin(rad)
    steps = max(2, int(length))
    for step in range(steps):
        t = step / steps
        px = int(x + (end_x - x) * t)
        py = int(y + (end_y - y) * t)
        light_factor = 0.5 + math.cos(rad) * 0.3
        random.seed(px * 73 + int(py / 5) * 131)
        bark_noise = (random.random() - 0.5) * 0.3
        thickness_factor = min(1.0, thickness / 18.0)
        random.seed(px * 17 + py * 29)
        crevasse_noise = math.sin(px * 0.5) * math.cos(py * 0.3) * 0.2
        brightness = light_factor + bark_noise + crevasse_noise
        brightness = max(0.0, min(1.0, brightness))
        color_index = int(brightness * 9)
        color_index = max(0, min(9, color_index))
        if thickness < 5:
            color_index = min(color_index, 4)
        elif thickness < 10:
            color_index = min(color_index, 6)
        target = lib.TREE_COLORS[color_index]
        pixel_color = lib.dither_pixel(px, py, target, lib.TREE_COLORS)
        thick_int = max(1, int(thickness))
        for dx in range(-thick_int // 2, thick_int // 2 + 1):
            for dy in range(-thick_int // 2, thick_int // 2 + 1):
                if 0 <= px + dx < surface.get_width() and 0 <= py + dy < surface.get_height():
                    edge_dist = math.sqrt(dx**2 + dy**2) / (thick_int / 2)
                    if edge_dist < 1.0:
                        random.seed((px + dx) * 41 + (py + dy) * 97)
                        edge_variation = (random.random() - 0.5) * 0.15
                        adjusted_brightness = brightness + edge_variation
                        adjusted_brightness = max(0.0, min(1.0, adjusted_brightness))
                        adj_color_index = int(adjusted_brightness * 9)
                        adj_color_index = max(0, min(9, adj_color_index))
                        if thickness < 5:
                            adj_color_index = min(adj_color_index, 4)
                        elif thickness < 10:
                            adj_color_index = min(adj_color_index, 6)
                        adj_target = lib.TREE_COLORS[adj_color_index]
                        adj_pixel_color = lib.dither_pixel(px + dx, py + dy, adj_target, lib.TREE_COLORS)
                        surface.set_at((px + dx, py + dy), adj_pixel_color)
    if depth < max_depth:
        base_spread = 25 if depth < 2 else 32
        angle_spread_left = base_spread
        angle_spread_right = base_spread
        length_factor = 0.7
        new_thickness = thickness * 0.7
        left_length = length * length_factor
        right_length = length * length_factor
        draw_tree_branch(surface, end_x, end_y, angle + angle_spread_left, 
                        left_length, new_thickness, depth + 1, max_depth, side_bias, wind_offset)
        draw_tree_branch(surface, end_x, end_y, angle - angle_spread_right, 
                        right_length, new_thickness, depth + 1, max_depth, side_bias, wind_offset)
        if depth >= 2:
            draw_tree_branch(surface, end_x, end_y, angle, 
                            length * 0.65, new_thickness * 0.85, depth + 1, max_depth, side_bias, wind_offset)


def create_tree(scene: lib.Scene, wind_offset=0):
    tree_surface = pygame.Surface((300, 350), pygame.SRCALPHA)
    base_x = 80
    base_y = 350
    draw_tree_branch(
        tree_surface,
        x=base_x,
        y=base_y,
        angle=90,
        length=100,
        thickness=18,
        depth=0,
        max_depth=7,
        side_bias=0.0,
        wind_offset=wind_offset
    )
    
    return tree_surface


def create_tree_animation(scene: lib.Scene):
    cache_dir = "tree_cache"
    num_frames = 40
    if os.path.exists(cache_dir):
        cached_files = [f for f in os.listdir(cache_dir) if f.endswith('.png')]
        
        if len(cached_files) == num_frames:
            print(f"Chargement de l'animation de l'arbre depuis le cache ({num_frames} frames)...")
            try:
                frames = []
                for i in range(num_frames):
                    frame_path = os.path.join(cache_dir, f"tree_frame_{i:03d}.png")
                    frame = pygame.image.load(frame_path).convert_alpha()
                    frames.append(frame)
                print("Animation de l'arbre chargée !")
                return frames
            except Exception as e:
                print(f"Erreur lors du chargement du cache : {e}")
                print("Régénération de l'animation...")
    
    print(f"Génération de l'animation de l'arbre ({num_frames} frames)...")
    frames = []
    for i in range(num_frames):
        t = (i / num_frames) * 2 * math.pi
        wind_offset = math.sin(t) * 2.5
        tree_frame = create_tree(scene, wind_offset)
        frames.append(tree_frame)
    try:
        print("Sauvegarde de l'animation dans le cache...")
        os.makedirs(cache_dir, exist_ok=True)
        
        for i, frame in enumerate(frames):
            frame_path = os.path.join(cache_dir, f"tree_frame_{i:03d}.png")
            pygame.image.save(frame, frame_path)
        
        print("Cache créé !")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du cache : {e}")
    
    print("Animation de l'arbre générée !")
    return frames


def game_init(scene: lib.Scene) -> List:
    width = scene.window_size[0]
    height = scene.window_size[1]
    print("=== INITIALISATION DU JEU ===")
    print(f"Résolution : {width}×{height}")
    print(f"FPS cible : {scene.tick}")
    print("Appuyez sur ECHAP pour quitter")
    print("============================")
    scene.static_background = create_static_background(scene)
    scene.middle_ground = create_middle_ground(scene)
    scene.snow_ground = create_snow_ground(scene)
    scene.tree_animation = create_tree_animation(scene)
    scene.snowfall = snowflakes.SnowfallSystem(width, height, num_flakes=25)
    print("Système de flocons de neige initialisé (25 flocons)")
    objects = []
    return objects


game = lib.Scene(
    width=640, 
    height=480, 
    init=game_init,
    prepaint=render_scene,
    tick=60
)
RUN = True
while RUN:
    RUN = game.mainloop()

print(f"\n=== FIN DU JEU ===")
print(f"Fenêtre fermée après {lib.loops} frames")
print(f"Durée totale : {game.time_game:.2f}s")
print(f"FPS moyen : {lib.loops / game.time_game:.1f}")

