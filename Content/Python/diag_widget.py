# diag_widget.py  -- print hard facts about UMG-tree python API on THIS engine build.
import unreal

def P(x):
    unreal.log("[DIAG] " + str(x))

FULL = "/Game/ArchVizExplorer/Blueprints/Widgets/BP_WeatherTime_Widget"

P("engine version: %s" % unreal.SystemLibrary.get_engine_version())

bp = unreal.load_asset(FULL)
P("bp repr: %r" % bp)
P("bp class name: %s" % (bp.get_class().get_name() if bp else "None"))

# What top-level UMG-building symbols exist?
for sym in ("WidgetTree", "WidgetBlueprint", "WidgetBlueprintLibrary",
            "WidgetBlueprintFactory", "PanelWidget", "UserWidget",
            "EditorUtilityWidgetBlueprint"):
    P("unreal.%s exists: %s" % (sym, hasattr(unreal, sym)))

# All methods/props on the bp object
if bp:
    meths = [m for m in dir(bp) if not m.startswith("__")]
    P("bp dir (%d): %s" % (len(meths), meths))

# WidgetTree class methods (does it expose construct_widget?)
if hasattr(unreal, "WidgetTree"):
    wt = [m for m in dir(unreal.WidgetTree) if not m.startswith("__")]
    P("unreal.WidgetTree dir: %s" % wt)

# WidgetBlueprintLibrary methods
if hasattr(unreal, "WidgetBlueprintLibrary"):
    wl = [m for m in dir(unreal.WidgetBlueprintLibrary) if not m.startswith("__")]
    P("unreal.WidgetBlueprintLibrary dir: %s" % wl)

# Try to read the tree off the generated-class CDO (compile first)
try:
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    P("compiled ok")
except Exception as e:
    P("compile failed: %s" % e)

gc = None
try:
    gc = bp.get_editor_property("generated_class")
except Exception as e:
    P("generated_class prop failed: %s" % e)
P("generated_class = %r" % gc)
if gc:
    try:
        cdo = unreal.get_default_object(gc)
        P("CDO = %r" % cdo)
        t = cdo.get_editor_property("widget_tree")
        P("CDO widget_tree = %r" % t)
        if t:
            P("CDO tree root = %r" % t.get_editor_property("root_widget"))
            P("CDO tree dir: %s" % [m for m in dir(t) if 'widget' in m.lower() or 'child' in m.lower()])
    except Exception as e:
        P("CDO route error: %s" % e)

P("DIAG DONE")
