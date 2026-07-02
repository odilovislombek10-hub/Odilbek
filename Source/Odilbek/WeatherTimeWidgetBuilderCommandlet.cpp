#include "WeatherTimeWidgetBuilderCommandlet.h"

#if WITH_EDITOR
#include "WidgetBlueprint.h"
#include "Blueprint/UserWidget.h"
#include "Blueprint/WidgetTree.h"
#include "Components/SizeBox.h"
#include "Components/Border.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/Button.h"
#include "Components/Image.h"
#include "Components/TextBlock.h"
#include "Components/Slider.h"
#include "Engine/Font.h"
#include "Engine/Texture2D.h"
#include "Styling/SlateColor.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Kismet2/KismetEditorUtilities.h"
#include "FileHelpers.h"
#endif

DEFINE_LOG_CATEGORY_STATIC(LogWeatherTimeBuilder, Log, All);

int32 UWeatherTimeWidgetBuilderCommandlet::Main(const FString& Params)
{
#if WITH_EDITOR
	const FString AssetName = TEXT("BP_WeatherTime_Widget");
	const FString ObjPath   = TEXT("/Game/ArchVizExplorer/Blueprints/Widgets/BP_WeatherTime_Widget.BP_WeatherTime_Widget");

	UWidgetBlueprint* WBP = LoadObject<UWidgetBlueprint>(nullptr, *ObjPath);
	if (!WBP)
	{
		UE_LOG(LogWeatherTimeBuilder, Error, TEXT("[WT] Could not load %s. Create the (empty) Widget Blueprint first."), *ObjPath);
		return 1;
	}

	UWidgetTree* Tree = WBP->WidgetTree;
	if (!Tree)
	{
		UE_LOG(LogWeatherTimeBuilder, Error, TEXT("[WT] WidgetTree is null"));
		return 1;
	}

	// Fresh rebuild: drop any existing widgets.
	Tree->RootWidget = nullptr;
	{
		TArray<UWidget*> All;
		Tree->GetAllWidgets(All);
		for (UWidget* W : All)
		{
			if (W) { Tree->RemoveWidget(W); }
		}
	}

	auto MakeFont = [](const TCHAR* FontPath, int32 Size) -> FSlateFontInfo
	{
		FSlateFontInfo Info;
		Info.FontObject = LoadObject<UObject>(nullptr, FontPath);
		Info.TypefaceFontName = TEXT("Default");
		Info.Size = Size;
		return Info;
	};

	const FSlateFontInfo FontTitle = MakeFont(TEXT("/Game/ArchVizExplorer/Fonts/FIRASANSCONDENSED_Font.FiraSansCondensed_Font"), 14);
	const FSlateFontInfo FontArrow = MakeFont(TEXT("/Game/ArchVizExplorer/Fonts/FIRASANSCONDENSED_Font.FiraSansCondensed_Font"), 20);
	const FSlateFontInfo FontTime  = MakeFont(TEXT("/Game/ArchVizExplorer/Fonts/ArchivoNarrow_Font.ArchivoNarrow_Font"), 26);

	const FLinearColor BtnBg(0.05f, 0.06f, 0.08f, 0.65f);
	const FLinearColor White09(1.f, 1.f, 1.f, 0.9f);

	// --- Root: SizeBox -> Border -> VerticalBox ---
	USizeBox* Root = Tree->ConstructWidget<USizeBox>(USizeBox::StaticClass(), TEXT("Root_SizeBox"));
	Root->SetWidthOverride(360.f);
	Tree->RootWidget = Root;

	UBorder* BorderRoot = Tree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("Border_Root"));
	BorderRoot->SetBrushColor(FLinearColor(0.f, 0.f, 0.f, 0.88f));
	BorderRoot->SetPadding(FMargin(14.f, 12.f, 14.f, 14.f));
	Root->SetContent(BorderRoot);

	UVerticalBox* VBox = Tree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("VBox_Main"));
	BorderRoot->SetContent(VBox);

	// --- Title ---
	UTextBlock* Title = Tree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("Text_Title"));
	Title->SetText(FText::FromString(TEXT("ПОГОДА  |  ВРЕМЯ СУТОК")));
	Title->SetFont(FontTitle);
	Title->SetColorAndOpacity(FSlateColor(White09));
	if (UVerticalBoxSlot* TS = Cast<UVerticalBoxSlot>(VBox->AddChild(Title)))
	{
		TS->SetPadding(FMargin(0, 0, 0, 10));
		TS->SetHorizontalAlignment(HAlign_Center);
	}

	// --- Time row: [<]  TextBlock_Time  [>] ---
	UHorizontalBox* TimeRow = Tree->ConstructWidget<UHorizontalBox>(UHorizontalBox::StaticClass(), TEXT("HBox_TimeRow"));

	auto MakeTextButton = [&](FName BtnName, const FString& Glyph) -> UButton*
	{
		UButton* Btn = Tree->ConstructWidget<UButton>(UButton::StaticClass(), BtnName);
		Btn->bIsVariable = true;
		Btn->SetBackgroundColor(BtnBg);
		UTextBlock* Lbl = Tree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), FName(*(FString(TEXT("Txt_")) + BtnName.ToString())));
		Lbl->SetText(FText::FromString(Glyph));
		Lbl->SetFont(FontArrow);
		Lbl->SetColorAndOpacity(FSlateColor(White09));
		Btn->SetContent(Lbl);
		return Btn;
	};

	UButton* BtnLeft = MakeTextButton(TEXT("Button_TimeLeft"), TEXT("◀"));
	if (UHorizontalBoxSlot* S = Cast<UHorizontalBoxSlot>(TimeRow->AddChild(BtnLeft)))
	{
		S->SetPadding(FMargin(2));
		S->SetVerticalAlignment(VAlign_Center);
	}

	UTextBlock* TimeText = Tree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("TextBlock_Time"));
	TimeText->bIsVariable = true;
	TimeText->SetText(FText::FromString(TEXT("16:00")));
	TimeText->SetFont(FontTime);
	TimeText->SetColorAndOpacity(FSlateColor(FLinearColor(1.f, 1.f, 1.f, 0.85f)));
	if (UHorizontalBoxSlot* S = Cast<UHorizontalBoxSlot>(TimeRow->AddChild(TimeText)))
	{
		S->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
		S->SetHorizontalAlignment(HAlign_Center);
		S->SetVerticalAlignment(VAlign_Center);
	}

	UButton* BtnRight = MakeTextButton(TEXT("Button_TimeRight"), TEXT("▶"));
	if (UHorizontalBoxSlot* S = Cast<UHorizontalBoxSlot>(TimeRow->AddChild(BtnRight)))
	{
		S->SetPadding(FMargin(2));
		S->SetVerticalAlignment(VAlign_Center);
	}

	if (UVerticalBoxSlot* S = Cast<UVerticalBoxSlot>(VBox->AddChild(TimeRow)))
	{
		S->SetPadding(FMargin(0, 0, 0, 6));
	}

	// --- Slider ---
	USlider* Slider = Tree->ConstructWidget<USlider>(USlider::StaticClass(), TEXT("Slider_TimeOfDay"));
	Slider->bIsVariable = true;
	Slider->SetMinValue(6.f);
	Slider->SetMaxValue(22.f);
	Slider->SetValue(16.f);
	Slider->SetSliderBarColor(FLinearColor(1.f, 1.f, 1.f, 0.8f));
	Slider->SetSliderHandleColor(FLinearColor::White);
	if (UVerticalBoxSlot* S = Cast<UVerticalBoxSlot>(VBox->AddChild(Slider)))
	{
		S->SetPadding(FMargin(2, 2, 2, 14));
	}

	// --- Icon button helper ---
	auto MakeIconButton = [&](FName BtnName, const TCHAR* TexPath) -> UButton*
	{
		UButton* Btn = Tree->ConstructWidget<UButton>(UButton::StaticClass(), BtnName);
		Btn->bIsVariable = true;
		Btn->SetBackgroundColor(BtnBg);
		UImage* Img = Tree->ConstructWidget<UImage>(UImage::StaticClass(), FName(*(FString(TEXT("Img_")) + BtnName.ToString())));
		if (UTexture2D* Tex = LoadObject<UTexture2D>(nullptr, TexPath))
		{
			Img->SetBrushFromTexture(Tex, false);
			FSlateBrush B = Img->GetBrush();
			B.ImageSize = FVector2D(40.f, 40.f);
			Img->SetBrush(B);
		}
		Img->SetColorAndOpacity(White09);
		Btn->SetContent(Img);
		return Btn;
	};

	// --- Weather row ---
	UHorizontalBox* WeatherRow = Tree->ConstructWidget<UHorizontalBox>(UHorizontalBox::StaticClass(), TEXT("HBox_Weather"));
	struct FBtnDef { const TCHAR* Name; const TCHAR* Tex; };
	const FBtnDef Weather[] = {
		{ TEXT("Button_Weather_Sun"),      TEXT("/Game/ArchVizExplorer/Textures/UI/Icons/T_Icon_Weather_Sun.T_Icon_Weather_Sun") },
		{ TEXT("Button_Weather_Cloud"),    TEXT("/Game/ArchVizExplorer/Textures/UI/Icons/T_Icon_Weather_Cloud.T_Icon_Weather_Cloud") },
		{ TEXT("Button_Weather_Overcast"), TEXT("/Game/ArchVizExplorer/Textures/UI/Icons/T_Icon_Weather_Overcast.T_Icon_Weather_Overcast") },
		{ TEXT("Button_Weather_Rain"),     TEXT("/Game/ArchVizExplorer/Textures/UI/Icons/T_Icon_Weather_Rain.T_Icon_Weather_Rain") },
	};
	for (const FBtnDef& D : Weather)
	{
		UButton* B = MakeIconButton(D.Name, D.Tex);
		if (UHorizontalBoxSlot* S = Cast<UHorizontalBoxSlot>(WeatherRow->AddChild(B)))
		{
			S->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
			S->SetPadding(FMargin(4));
			S->SetHorizontalAlignment(HAlign_Fill);
			S->SetVerticalAlignment(VAlign_Fill);
		}
	}
	if (UVerticalBoxSlot* S = Cast<UVerticalBoxSlot>(VBox->AddChild(WeatherRow)))
	{
		S->SetPadding(FMargin(0, 0, 0, 8));
	}

	// --- Season row ---
	UHorizontalBox* SeasonRow = Tree->ConstructWidget<UHorizontalBox>(UHorizontalBox::StaticClass(), TEXT("HBox_Season"));
	const FBtnDef Season[] = {
		{ TEXT("Button_Season_Summer"), TEXT("/Game/ArchVizExplorer/Textures/UI/Icons/T_Icon_Season_Summer.T_Icon_Season_Summer") },
		{ TEXT("Button_Season_Autumn"), TEXT("/Game/ArchVizExplorer/Textures/UI/Icons/T_Icon_Season_Autumn.T_Icon_Season_Autumn") },
		{ TEXT("Button_Season_Winter"), TEXT("/Game/ArchVizExplorer/Textures/UI/Icons/T_Icon_Season_Winter.T_Icon_Season_Winter") },
	};
	for (const FBtnDef& D : Season)
	{
		UButton* B = MakeIconButton(D.Name, D.Tex);
		if (UHorizontalBoxSlot* S = Cast<UHorizontalBoxSlot>(SeasonRow->AddChild(B)))
		{
			S->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
			S->SetPadding(FMargin(4));
			S->SetHorizontalAlignment(HAlign_Fill);
			S->SetVerticalAlignment(VAlign_Fill);
		}
	}
	VBox->AddChild(SeasonRow);

	// --- Persist ---
	FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(WBP);
	FKismetEditorUtilities::CompileBlueprint(WBP);

	TArray<UPackage*> Packages;
	Packages.Add(WBP->GetOutermost());
	UEditorLoadingAndSavingUtils::SavePackages(Packages, /*bOnlyDirty=*/false);

	UE_LOG(LogWeatherTimeBuilder, Display, TEXT("[WT] BUILD DONE -> %s"), *ObjPath);
	return 0;
#else
	UE_LOG(LogWeatherTimeBuilder, Error, TEXT("[WT] Editor-only commandlet."));
	return 1;
#endif
}
