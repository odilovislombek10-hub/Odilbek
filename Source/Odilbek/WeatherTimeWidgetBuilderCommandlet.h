// Editor helper that builds the BP_WeatherTime_Widget UMG tree from C++.
// UMG widget trees cannot be constructed from Python/automation (WidgetTree is
// not script-exposed), so this native function does it. Invoke from the Editor:
//   import unreal; unreal.OdilbekWidgetBuilderLibrary.build_weather_time_widget()
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "WeatherTimeWidgetBuilderCommandlet.generated.h"

UCLASS()
class UOdilbekWidgetBuilderLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	// Builds (or rebuilds) /Game/ArchVizExplorer/Blueprints/Widgets/BP_WeatherTime_Widget.
	UFUNCTION(BlueprintCallable, Category = "Odilbek")
	static void BuildWeatherTimeWidget();
};
