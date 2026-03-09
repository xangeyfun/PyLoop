

const scriptsInEvents = {

	async EventSheet1_Event4_Act1(runtime, localVars)
	{
		alert("Connection to the save server failed. The game is running in offline mode, so progress will not be saved. Create or log in to your account at https://pyloop.nexohub.ddns.net/ to enable saving.");
	},

	async EventSheet1_Event5_Act1(runtime, localVars)
	{
		alert("Connection to the save server failed. The game is running in offline mode, so progress will not be saved. Create or log in to your account at https://pyloop.nexohub.ddns.net/ to enable saving.");
	},

	async EventSheet1_Event8_Act1(runtime, localVars)
	{
		const LOC_Counter = runtime.objects.LOC_Counter?.getFirstInstance();
		const LOC_Sec = runtime.objects.LOC_Sec?.getFirstInstance();
		
		const Upgrade1Price = runtime.objects.Upgrade1Price?.getFirstInstance();
		const Upgrade1Text = runtime.objects.Upgrade1Text?.getFirstInstance();
		
		const Upgrade2Price = runtime.objects.Upgrade2Price?.getFirstInstance();
		const Upgrade2Text = runtime.objects.Upgrade2Text?.getFirstInstance();
		
		const Upgrade3Price = runtime.objects.Upgrade3Price?.getFirstInstance();
		const Upgrade3Text = runtime.objects.Upgrade3Text?.getFirstInstance();
		
		const LOCUpgrade1Price = runtime.objects.LOCUpgrade1Price?.getFirstInstance();
		const LOCUpgrade1Text = runtime.objects.LOCUpgrade1Text?.getFirstInstance();
		
		const LOCUpgrade2Price = runtime.objects.LOCUpgrade2Price?.getFirstInstance();
		const LOCUpgrade2Text = runtime.objects.LOCUpgrade2Text?.getFirstInstance();
		
		const LOCUpgrade3Price = runtime.objects.LOCUpgrade3Price?.getFirstInstance();
		const LOCUpgrade3Text = runtime.objects.LOCUpgrade3Text?.getFirstInstance();
		
		const LOCPERCLICK = runtime.objects.LOCPERCLICK?.getFirstInstance();
		
		
		function Format(num) {
		    if (num >= 1e12) return (num / 1e12).toFixed(1) + "T";
		    if (num >= 1e9)  return (num / 1e9).toFixed(1) + "B";
		    if (num >= 1e6)  return (num / 1e6).toFixed(1) + "M";
		    if (num >= 1e3)  return (num / 1e3).toFixed(1) + "K";
		    return num.toString();
		}
		
		if (LOC_Counter)
		    LOC_Counter.text = Format(runtime.globalVars.LOC) + " LOC";
		
		if (LOC_Sec)
		    LOC_Sec.text = Format(runtime.globalVars.LOCPerSecond) + " LOC/sec";
		
		if (LOCPERCLICK)
		    LOCPERCLICK.text = Format(runtime.globalVars.ClickValue) + " LOC per click";
		
		if (Upgrade1Price)
		    Upgrade1Price.text = Format(runtime.globalVars.Upgrade1Price);
		
		if (Upgrade1Text)
		    Upgrade1Text.text = "Auto Indentation (" + (runtime.globalVars.Upgrade1Owned - 1) + ")";
		
		if (Upgrade2Price)
		    Upgrade2Price.text = Format(runtime.globalVars.Upgrade2Price);
		
		if (Upgrade2Text)
		    Upgrade2Text.text = "StackOverflow (" + (runtime.globalVars.Upgrade2Owned - 1) + ")";
		
		if (Upgrade3Price)
		    Upgrade3Price.text = Format(runtime.globalVars.Upgrade3Price);
		
		if (Upgrade3Text)
		    Upgrade3Text.text = "AI Autocomplete (" + (runtime.globalVars.Upgrade3Owned - 1) + ")";
		
		if (LOCUpgrade1Price)
		    LOCUpgrade1Price.text = Format(runtime.globalVars.LOCUpgrade1Price);
		
		if (LOCUpgrade1Text)
		    LOCUpgrade1Text.text = "For loop (" + (runtime.globalVars.LOCUpgrade1Owned - 1) + ")";
		
		if (LOCUpgrade2Price)
		    LOCUpgrade2Price.text = Format(runtime.globalVars.LOCUpgrade2Price);
		
		if (LOCUpgrade2Text)
		    LOCUpgrade2Text.text = "Functions (" + (runtime.globalVars.LOCUpgrade2Owned - 1) + ")";
		
		if (LOCUpgrade3Price)
		    LOCUpgrade3Price.text = Format(runtime.globalVars.LOCUpgrade3Price);
		
		if (LOCUpgrade3Text)
		    LOCUpgrade3Text.text = "AI code (" + (runtime.globalVars.LOCUpgrade3Owned - 1) + ")";
	},

	async EventSheet1_Event9_Act7(runtime, localVars)
	{
		const visual = runtime.objects.visual?.getFirstInstance();
		
		function Format(num) {
		    if (num >= 1e12) return (num / 1e12).toFixed(1) + "T";
		    if (num >= 1e9)  return (num / 1e9).toFixed(1) + "B";
		    if (num >= 1e6)  return (num / 1e6).toFixed(1) + "M";
		    if (num >= 1e3)  return (num / 1e3).toFixed(1) + "K";
		    return num.toString();
		}
		
		if (visual)
		    visual.text = "+" + Format(runtime.globalVars.ClickValue)
	}
};

globalThis.C3.JavaScriptInEvents = scriptsInEvents;
