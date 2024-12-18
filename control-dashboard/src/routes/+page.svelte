<script lang="ts">
	import Footer from '$lib/components/footer.svelte';
	import Navbar from '$lib/components/navbar.svelte';
	import Settings from '$lib/components/syncflow-settings.svelte';
	import type { PageData } from '$lib/types';

	let { data }: { data: PageData } = $props();

	let settings = data.settings;
</script>

<header
	class="sticky top-0 z-40 mx-auto w-full flex-none border-b border-gray-200 bg-white dark:border-gray-600 dark:bg-gray-900"
>
	<Navbar />
</header>
<main
	class="h-full min-w-0 flex-auto divide-y lg:static lg:max-h-full lg:overflow-visible dark:divide-gray-700 dark:bg-gray-900"
>
	<Settings
		enableScreenShare={settings.enableScreenShare}
		sessionName={settings.sessionName}
		enabled={settings.enabled}
		enableAudio={settings.enableAudio}
		enableCamera={settings.enableCamera}
	/>
	<Footer />
</main>
