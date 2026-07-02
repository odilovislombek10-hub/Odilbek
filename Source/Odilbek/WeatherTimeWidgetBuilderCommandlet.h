// Editor-only commandlet that builds the BP_WeatherTime_Widget UMG tree.
// Run headless (editor closed) with:
//   UnrealEditor-Cmd.exe <Project.uproject> -run=WeatherTimeWidgetBuilder
#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "WeatherTimeWidgetBuilderCommandlet.generated.h"

UCLASS()
class UWeatherTimeWidgetBuilderCommandlet : public UCommandlet
{
	GENERATED_BODY()

public:
	virtual int32 Main(const FString& Params) override;
};
