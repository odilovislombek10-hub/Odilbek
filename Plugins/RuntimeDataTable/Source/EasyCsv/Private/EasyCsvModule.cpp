// Copyright Jared Therriault 2019, 2022

#include "EasyCsvModule.h"

#include "EasyCsvProjectSettings.h"

#include "Misc/CoreDelegates.h"
#include "UnrealEngine.h"
#include "Developer/Settings/Public/ISettingsModule.h"
#include "Modules/ModuleManager.h"
#include "UnrealEngine.h"

IMPLEMENT_MODULE(FEasyCsvModule, EasyCsv);

void FEasyCsvModule::StartupModule()
{
	UE_LOG(LogEasyCsv, Log, TEXT("Module Startup"));

	FCoreDelegates::OnFEngineLoopInitComplete.AddRaw(this, &FEasyCsvModule::OnFEngineLoopInitComplete);
}

void FEasyCsvModule::ShutdownModule()
{
	UnregisterProjectSettings();
	
	UE_LOG(LogEasyCsv, Log, TEXT("Module Shutdown"));
}

void FEasyCsvModule::RegisterProjectSettings() const
{
	if (ISettingsModule* SettingsModule = FModuleManager::GetModulePtr<ISettingsModule>("Settings"))
	{
		const TSharedPtr<ISettingsSection> ProjectSettingsSectionPtr = SettingsModule->RegisterSettings(
		"Project", "Plugins", "easyCSV",
		NSLOCTEXT("easyCSV", "easyCSVSettingsCategoryDisplayName", "easyCSV"),
		NSLOCTEXT("easyCSV", "easyCSVSettingsDescription",
				  "Configure the easyCSV user settings"),
		GetMutableDefault<UEasyCsvProjectSettings>());
	}
}

void FEasyCsvModule::UnregisterProjectSettings() const
{
	if (ISettingsModule* SettingsModule = FModuleManager::GetModulePtr<ISettingsModule>("Settings"))
	{
		SettingsModule->UnregisterSettings("Project", "Plugins", "easyCSV");
	}
}

void FEasyCsvModule::Print(FString InMessage, const ELogType InLogType)
{
	const UEasyCsvProjectSettings* ProjectSettings = GetDefault<UEasyCsvProjectSettings>();
	check(ProjectSettings);

	const int32 Limit = ProjectSettings->LogCharacterLimit;
	if (Limit > -1 && InMessage.Len() > Limit)
	{
		InMessage.LeftInline(Limit);
	}
	
	if (GEngine)
	{
		if (InLogType == ELogType::Display && ProjectSettings->bPrintDisplayMessagesToScreen)
		{
			const FString Message = "Info: " + InMessage;
			GEngine->AddOnScreenDebugMessage(
				INDEX_NONE, ProjectSettings->DisplayMessagesOnScreenLifetime, FColor::White, Message);
		}
		else if (InLogType == ELogType::Warning && ProjectSettings->bPrintWarningMessagesToScreen)
		{
			const FString Message = "Warning: " + InMessage;
			GEngine->AddOnScreenDebugMessage(
				INDEX_NONE, ProjectSettings->WarningMessagesOnScreenLifetime, FColor::Yellow, Message);
		}
		else if (InLogType == ELogType::Error && ProjectSettings->bPrintErrorMessagesToScreen)
		{
			const FString Message = "Error: " + InMessage;
			GEngine->AddOnScreenDebugMessage(
				INDEX_NONE, ProjectSettings->ErrorMessagesOnScreenLifetime, FColor::Red, Message);
		}
	}
	

	if (InLogType == ELogType::Display && ProjectSettings->bPrintDisplayMessagesToLog)
	{
		FEasyCsvModule::PrintToLog(InMessage);
	}
	else if (InLogType == ELogType::Warning && ProjectSettings->bPrintWarningMessagesToLog)
	{
		FEasyCsvModule::PrintWarningToLog(InMessage);
	}
	else if (InLogType == ELogType::Error && ProjectSettings->bPrintErrorMessagesToLog)
	{
		FEasyCsvModule::PrintErrorToLog(InMessage);
	}
}

void FEasyCsvModule::OnFEngineLoopInitComplete()
{
	RegisterProjectSettings();
}

void FEasyCsvModule::PrintToLog(const FString& LogMessage)
{
	UE_LOG(LogEasyCsv, Log, TEXT("%s"), *LogMessage);
}

void FEasyCsvModule::PrintWarningToLog(const FString& LogMessage)
{
	UE_LOG(LogEasyCsv, Warning, TEXT("%s"), *LogMessage);
}

void FEasyCsvModule::PrintErrorToLog(const FString& LogMessage)
{
	UE_LOG(LogEasyCsv, Error, TEXT("%s"), *LogMessage);
}
