<!-- Export tye syncFlow settings Type -->
<script module lang="ts">
	export interface SyncFlowSettings {
		enabled: boolean;
		enableAudio: boolean;
		enableCamera: boolean;
		enableScreenShare: boolean;
		sessionName: string | null;
	}
</script>

<script lang="ts">
	import { Toggle } from 'flowbite-svelte';
	import { dev } from '$app/environment';
	import { base } from '$app/paths';

	let settings = $props();
	let currentSettings = $state(settings);
	let settingsState = $state({
		enabled: settings.enabled,
		enableAudio: settings.enableAudio,
		enableCamera: settings.enableCamera,
		enableScreenShare: settings.enableScreenShare,
		sessionName: settings.sessionName
	});

	let enableUpdate = $derived.by(() => {
		return (
			currentSettings.enabled !== settingsState.enabled ||
			currentSettings.enableAudio !== settingsState.enableAudio ||
			currentSettings.enableCamera !== settingsState.enableCamera ||
			currentSettings.enableScreenShare !== settingsState.enableScreenShare ||
			currentSettings.sessionName !== settingsState.sessionName
		);
	});

	async function updateSettings() {
		const baseUrl = dev ? '/api' : '';

		const response = await fetch(`${baseUrl}/syncflow/runtime-settings`, {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify($state.snapshot(settingsState))
		});

		if (response.ok) {
			currentSettings = await response.json();
		} else {
			alert('Failed to update settings');
		}
	}
</script>

<div class="max-w-8xl mx-auto flex flex-col px-6 py-6 lg:px-6 lg:py-6">
	<h2 class="text-2xl font-semibold text-gray-900 dark:text-gray-300">SyncFlow Settings</h2>

	<div class="mt-6 flex flex-row text-gray-900 dark:text-gray-300">
		<span>{settingsState.enabled ? 'Disable' : 'Enable'} SyncFlow Pipeline</span>
		<Toggle bind:checked={settingsState.enabled} class="ms-auto" />
	</div>
	{#if settingsState.enabled}
		<Toggle bind:checked={settingsState.enableAudio} class="mt-6">Enable Audio Sharing</Toggle>
		<Toggle bind:checked={settingsState.enableCamera} class="mt-6">Enable Camera Sharing</Toggle>
		<Toggle bind:checked={settingsState.enableScreenShare} class="mt-6"
			>Enable Screen Sharing</Toggle
		>
		<input
			type="text"
			bind:value={settingsState.sessionName}
			class="mt-6 w-full rounded-lg border border-gray-300 px-4 py-2 text-gray-900 dark:bg-gray-800 dark:text-gray-300"
			placeholder="Session Name"
		/>
	{/if}
	{#if enableUpdate}
		<button
			class="mt-6 rounded-lg bg-primary-700 px-4 py-2 font-semibold text-white"
			onclick={updateSettings}>Update Settings</button
		>
	{/if}
</div>
