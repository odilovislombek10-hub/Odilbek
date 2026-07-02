# build_weather_time_widget.py
# Builds /Game/ArchVizExplorer/Blueprints/Widgets/BP_WeatherTime_Widget  UMG tree.
# Run once inside the Unreal Editor (Output Log > Python, or the bottom Python cmd bar:
#   type this file's path, or:  exec(open(r'<path>').read())
# MCP tooling cannot build UMG widget trees, so this native-Editor-Python step does it.
# Idempotent: if the widget already exists it rebuilds its tree from scratch.

import unreal

PKG_PATH   = "/Game/ArchVizExplorer/Blueprints/Widgets"
ASSET_NAME = "BP_WeatherTime_Widget"
FULL_PATH  = PKG_PATH + "/" + ASSET_NAME

FONT_TITLE = "/Game/ArchVizExplorer/Fonts/FIRASANSCONDENSED_Font"
FONT_TIME  = "/Game/ArchVizExplorer/Fonts/ArchivoNarrow_Font"

ICON = {
    "Sun":      "/Game/ArchVizExplorer/Textures/UI/Icons/T_Icon_Weather_Sun",
    "Cloud":    "/Game/ArchVizExplorer/Textures/UI/Icons/T_Icon_Weather_Cloud",
    "Overcast": "/Game/ArchVizExplorer/Textures/UI/Icons/T_Icon_Weather_Overcast",
    "Rain":     "/Game/ArchVizExplorer/Textures/UI/Icons/T_Icon_Weather_Rain",
    "Summer":   "/Game/ArchVizExplorer/Textures/UI/Icons/T_Icon_Season_Summer",
    "Autumn":   "/Game/ArchVizExplorer/Textures/UI/Icons/T_Icon_Season_Autumn",
    "Winter":   "/Game/ArchVizExplorer/Textures/UI/Icons/T_Icon_Season_Winter",
}

eal = unreal.EditorAssetLibrary


def log(msg):
    unreal.log("[WeatherTime] " + str(msg))


def make_font(path, size):
    f = unreal.load_asset(path)
    sfi = unreal.SlateFontInfo()
    sfi.set_editor_property("font_object", f)
    sfi.set_editor_property("typeface_font_name", "Default")
    sfi.set_editor_property("size", size)
    return sfi


def set_is_var(w, name):
    w.rename(name)
    try:
        w.set_editor_property("is_variable", True)
    except Exception:
        try:
            w.set_editor_property("b_is_variable", True)
        except Exception as e:
            log("is_variable set failed for %s: %s" % (name, e))


def get_or_create_bp():
    if eal.does_asset_exist(FULL_PATH):
        log("asset exists, loading")
        return unreal.load_asset(FULL_PATH)
    factory = unreal.WidgetBlueprintFactory()
    factory.set_editor_property("parent_class", unreal.UserWidget)
    at = unreal.AssetToolsHelpers.get_asset_tools()
    bp = at.create_asset(ASSET_NAME, PKG_PATH, None, factory)
    log("created new widget blueprint")
    return bp


def clear_tree(tree):
    root = tree.get_editor_property("root_widget")
    if root:
        try:
            tree.set_editor_property("root_widget", None)
        except Exception as e:
            log("could not clear root: %s" % e)


def white(a=1.0):
    return unreal.LinearColor(1.0, 1.0, 1.0, a)


def make_icon_button(tree, btn_name, tex_path):
    btn = tree.construct_widget(unreal.Button, unreal.Name(btn_name))
    btn.set_background_color(unreal.LinearColor(0.05, 0.06, 0.08, 0.65))
    img = tree.construct_widget(unreal.Image, unreal.Name("Img_" + btn_name))
    tex = unreal.load_asset(tex_path)
    img.set_brush_from_texture(tex, False)
    img.set_brush_size(unreal.Vector2D(40.0, 40.0))
    img.set_color_and_opacity(white(0.9))
    btn.set_content(img)
    set_is_var(btn, btn_name)
    return btn


def make_text_button(tree, btn_name, glyph, font):
    btn = tree.construct_widget(unreal.Button, unreal.Name(btn_name))
    btn.set_background_color(unreal.LinearColor(0.05, 0.06, 0.08, 0.65))
    t = tree.construct_widget(unreal.TextBlock, unreal.Name("Txt_" + btn_name))
    t.set_text(glyph)
    t.set_font(font)
    t.set_color_and_opacity(unreal.SlateColor(white(0.9)))
    btn.set_content(t)
    set_is_var(btn, btn_name)
    return btn


def fill_slot(slot, pad=4.0):
    try:
        slot.set_size(unreal.SlateChildSize(1.0, unreal.SlateSizeRule.FILL))
    except Exception:
        pass
    try:
        slot.set_padding(unreal.Margin(pad, pad, pad, pad))
    except Exception:
        pass
    try:
        slot.set_horizontal_alignment(unreal.HorizontalAlignment.H_ALIGN_FILL)
        slot.set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_FILL)
    except Exception:
        pass


def build():
    bp = get_or_create_bp()
    tree = bp.get_editor_property("widget_tree")
    clear_tree(tree)

    font_title = make_font(FONT_TITLE, 14)
    font_time  = make_font(FONT_TIME, 26)
    font_arrow = make_font(FONT_TITLE, 20)

    # Root: SizeBox (fixed width) -> Border (dark) -> VerticalBox
    sizebox = tree.construct_widget(unreal.SizeBox, unreal.Name("Root_SizeBox"))
    sizebox.set_width_override(360.0)
    tree.set_editor_property("root_widget", sizebox)

    border = tree.construct_widget(unreal.Border, unreal.Name("Border_Root"))
    border.set_brush_color(unreal.LinearColor(0.0, 0.0, 0.0, 0.88))
    border.set_padding(unreal.Margin(14.0, 12.0, 14.0, 14.0))
    sizebox.set_content(border)

    vbox = tree.construct_widget(unreal.VerticalBox, unreal.Name("VBox_Main"))
    border.set_content(vbox)

    # --- Title ---
    title = tree.construct_widget(unreal.TextBlock, unreal.Name("Text_Title"))
    title.set_text("ПОГОДА  |  ВРЕМЯ СУТОК")
    title.set_font(font_title)
    title.set_color_and_opacity(unreal.SlateColor(white(0.9)))
    s = vbox.add_child_to_vertical_box(title)
    try:
        s.set_padding(unreal.Margin(0, 0, 0, 10))
        s.set_horizontal_alignment(unreal.HorizontalAlignment.H_ALIGN_CENTER)
    except Exception:
        pass

    # --- Time row: [<]  00:00  [>] ---
    time_row = tree.construct_widget(unreal.HorizontalBox, unreal.Name("HBox_TimeRow"))
    bl = make_text_button(tree, "Button_TimeLeft", "◀", font_arrow)
    fill_slot(time_row.add_child_to_horizontal_box(bl), 2.0)
    ttime = tree.construct_widget(unreal.TextBlock, unreal.Name("TextBlock_Time"))
    ttime.set_text("16:00")
    ttime.set_font(font_time)
    ttime.set_color_and_opacity(unreal.SlateColor(white(0.85)))
    set_is_var(ttime, "TextBlock_Time")
    ct = time_row.add_child_to_horizontal_box(ttime)
    try:
        ct.set_size(unreal.SlateChildSize(1.0, unreal.SlateSizeRule.FILL))
        ct.set_horizontal_alignment(unreal.HorizontalAlignment.H_ALIGN_CENTER)
        ct.set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_CENTER)
    except Exception:
        pass
    br = make_text_button(tree, "Button_TimeRight", "▶", font_arrow)
    fill_slot(time_row.add_child_to_horizontal_box(br), 2.0)
    sr = vbox.add_child_to_vertical_box(time_row)
    try:
        sr.set_padding(unreal.Margin(0, 0, 0, 6))
    except Exception:
        pass

    # --- Slider ---
    slider = tree.construct_widget(unreal.Slider, unreal.Name("Slider_TimeOfDay"))
    slider.set_min_value(6.0)
    slider.set_max_value(22.0)
    slider.set_value(16.0)
    try:
        slider.set_editor_property("slider_bar_color", white(0.8))
        slider.set_editor_property("slider_handle_color", white(1.0))
    except Exception:
        pass
    set_is_var(slider, "Slider_TimeOfDay")
    ss = vbox.add_child_to_vertical_box(slider)
    try:
        ss.set_padding(unreal.Margin(2, 2, 2, 14))
    except Exception:
        pass

    # --- Weather row ---
    weather_row = tree.construct_widget(unreal.HorizontalBox, unreal.Name("HBox_Weather"))
    for key, bname in (("Sun", "Button_Weather_Sun"), ("Cloud", "Button_Weather_Cloud"),
                       ("Overcast", "Button_Weather_Overcast"), ("Rain", "Button_Weather_Rain")):
        b = make_icon_button(tree, bname, ICON[key])
        fill_slot(weather_row.add_child_to_horizontal_box(b), 4.0)
    sw = vbox.add_child_to_vertical_box(weather_row)
    try:
        sw.set_padding(unreal.Margin(0, 0, 0, 8))
    except Exception:
        pass

    # --- Season row ---
    season_row = tree.construct_widget(unreal.HorizontalBox, unreal.Name("HBox_Season"))
    for key, bname in (("Summer", "Button_Season_Summer"), ("Autumn", "Button_Season_Autumn"),
                       ("Winter", "Button_Season_Winter")):
        b = make_icon_button(tree, bname, ICON[key])
        fill_slot(season_row.add_child_to_horizontal_box(b), 4.0)
    vbox.add_child_to_vertical_box(season_row)

    # Compile + save
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    except Exception as e:
        log("compile via BlueprintEditorLibrary failed: %s" % e)
    eal.save_asset(FULL_PATH)
    log("BUILD DONE -> " + FULL_PATH)


try:
    build()
except Exception:
    import traceback
    unreal.log_error("[WeatherTime] BUILD FAILED:\n" + traceback.format_exc())
