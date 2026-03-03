

const scriptsInEvents = {

	async EventSheet1_Event5_Act1(runtime, localVars)
	{
		alert("Connection to the save server failed. The game is running in offline mode, so progress will not be saved. Create or log in to your account at https://pyloop.nexohub.ddns.net/ to enable saving.");
	},

	async EventSheet1_Event6_Act1(runtime, localVars)
	{
		alert("Connection to the save server failed. The game is running in offline mode, so progress will not be saved. Create or log in to your account at https://pyloop.nexohub.ddns.net/ to enable saving.");
	}
};

globalThis.C3.JavaScriptInEvents = scriptsInEvents;
