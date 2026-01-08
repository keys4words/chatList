from PIL import Image, ImageDraw, ImageFont
import math

def draw_icon(size):
    """Рисует пиктограмму искусственного интеллекта на темном фоне."""
    # Создаем RGB изображение с темным фоном (темно-синий/черный)
    img = Image.new("RGB", (size, size), (20, 25, 40))  # Темный фон
    draw = ImageDraw.Draw(img)
    
    center_x = size // 2
    center_y = size // 2
    
    # Основные цвета
    primary_color = (100, 150, 255)  # Яркий синий для AI элементов
    accent_color = (150, 200, 255)   # Светло-синий для акцентов
    glow_color = (60, 100, 200)      # Средний синий для свечения
    
    # Рисуем абстрактную нейронную сеть / мозг
    # Центральный узел (мозг)
    node_radius = int(size * 0.15)
    draw.ellipse(
        [center_x - node_radius, center_y - node_radius,
         center_x + node_radius, center_y + node_radius],
        fill=primary_color,
        outline=accent_color,
        width=max(1, size // 64)
    )
    
    # Внутренний круг для эффекта свечения
    inner_radius = int(node_radius * 0.6)
    draw.ellipse(
        [center_x - inner_radius, center_y - inner_radius,
         center_x + inner_radius, center_y + inner_radius],
        fill=accent_color
    )
    
    # Периферийные узлы (нейроны)
    num_nodes = 6
    outer_radius = int(size * 0.35)
    node_size = int(size * 0.08)
    
    for i in range(num_nodes):
        angle = (2 * math.pi * i) / num_nodes
        node_x = center_x + int(outer_radius * math.cos(angle))
        node_y = center_y + int(outer_radius * math.sin(angle))
        
        # Рисуем узел
        draw.ellipse(
            [node_x - node_size, node_y - node_size,
             node_x + node_size, node_y + node_size],
            fill=glow_color,
            outline=primary_color,
            width=max(1, size // 128)
        )
        
        # Соединяем центральный узел с периферийными
        draw.line(
            [center_x, center_y, node_x, node_y],
            fill=primary_color,
            width=max(1, size // 128)
        )
    
    # Дополнительные связи между периферийными узлами (создают сеть)
    for i in range(num_nodes):
        angle1 = (2 * math.pi * i) / num_nodes
        node1_x = center_x + int(outer_radius * math.cos(angle1))
        node1_y = center_y + int(outer_radius * math.sin(angle1))
        
        # Соединяем с соседними узлами
        for j in range(1, 3):  # Соединяем с 2 соседними
            next_i = (i + j) % num_nodes
            angle2 = (2 * math.pi * next_i) / num_nodes
            node2_x = center_x + int(outer_radius * math.cos(angle2))
            node2_y = center_y + int(outer_radius * math.sin(angle2))
            
            # Тонкие линии для сетевых связей
            draw.line(
                [node1_x, node1_y, node2_x, node2_y],
                fill=glow_color,
                width=max(1, size // 256)
            )
    
    # Добавляем символ "AI" в центре (опционально, для больших размеров)
    if size >= 64:
        try:
            # Пытаемся использовать системный шрифт
            font_size = max(8, size // 8)
            # Используем простой шрифт по умолчанию
            font = ImageFont.load_default()
            
            # Рисуем букву "A" в центре
            text = "A"
            # Получаем размер текста
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Рисуем текст в центре
            text_x = center_x - text_width // 2
            text_y = center_y - text_height // 2
            
            # Рисуем с обводкой для лучшей видимости
            for adj in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                draw.text(
                    (text_x + adj[0], text_y + adj[1]),
                    text,
                    fill=(20, 25, 40),  # Темный цвет для обводки
                    font=font
                )
            draw.text(
                (text_x, text_y),
                text,
                fill=accent_color,  # Светлый цвет для текста
                font=font
            )
        except:
            # Если не удалось нарисовать текст, просто пропускаем
            pass
    
    return img

# Размеры иконки
sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
icons = [draw_icon(s) for s, _ in sizes]

# Изображения уже в RGB режиме, просто убеждаемся
rgb_icons = []
for icon in icons:
    # Убеждаемся, что изображение в RGB режиме (не палитра)
    if icon.mode != "RGB":
        rgb_img = icon.convert("RGB")
    else:
        rgb_img = icon
    rgb_icons.append(rgb_img)

# Сохранение с явным указанием формата и цветов
# ВАЖНО: Изображения уже в RGB режиме с темным фоном, что гарантирует
# сохранение цветов и избегает автоматической конвертации в градации серого
try:
    rgb_icons[0].save(
        "app.ico",
        format="ICO",
        sizes=sizes,
        append_images=rgb_icons[1:]
    )
    print("✅ Иконка 'app.ico' создана!")
    print("   Дизайн: пиктограмма искусственного интеллекта")
    print("   Элементы: нейронная сеть с центральным узлом и периферийными узлами")
    print("   Цвета: темный фон, яркие синие элементы (AI символ)")
except Exception as e:
    print(f"❌ Ошибка при сохранении: {e}")
    # Альтернативный способ - сохранить каждое изображение отдельно
    print("Попытка альтернативного метода сохранения...")
    rgb_icons[0].save("app.ico", format="ICO")
    print("✅ Иконка 'app.ico' создана (только один размер)")