<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import {
		Button,
		DarkMode,
		Navbar,
		NavBrand,
		NavHamburger,
		NavLi,
		NavUl,
		Tooltip
	} from 'flowbite-svelte';
	import { base } from '$app/paths';
	import { dev } from '$app/environment';

	let drawerHiddenStore = $state(true);

	let divClass = 'w-full ms-auto lg:block lg:w-auto order-1 lg:order-none';
	let ulClass =
		'flex flex-col py-3 my-4 lg:flex-row lg:my-0 text-sm font-medium text-gray-900 dark:text-gray-300 gap-4';
	let logo = base + '/logo.png';

	const toggleDrawer = () => {
		drawerHiddenStore = !drawerHiddenStore;
	};

	let activeUrl = $derived(page.route.id);

	async function signOut() {
		const baseUrl = dev ? '/api' : '';
		let resonse = await fetch(`${baseUrl}/admin/logout`, { method: 'POST' });
		if (resonse.ok) {
			goto(`${base}/login`);
		} else {
			alert('Logout failed\n' + (await resonse.text()));
		}
	}
</script>

<Navbar color="default" fluid class="max-w-8xl mx-auto py-1.5 lg:px-0 dark:bg-gray-900" let:toggle>
	<span>
		<NavHamburger onClick={toggleDrawer} class="m-0 me-3 md:block lg:hidden" />
	</span>
	<NavBrand href={base}>
		<img src={logo} class="me-3 h-8" alt="Food Justice Logo" />
		<span class="self-center whitespace-nowrap text-2xl font-semibold text-gray-900 dark:text-white"
			>FoodJustice Settings</span
		>
	</NavBrand>

	<NavUl
		{divClass}
		{ulClass}
		{activeUrl}
		on:click={() => setTimeout(toggle, 1)}
		nonActiveClass="md:!ps-3 md:!py-2 lg:!ps-0 text-gray-700 hover:bg-gray-100 lg:hover:bg-transparent lg:border-0 lg:hover:text-primary-700 dark:text-gray-400 lg:dark:text-white lg:dark:hover:text-primary-700 dark:hover:bg-gray-700 dark:hover:text-white lg:dark:hover:bg-transparent"
		activeClass="md:!ps-3 md:!py-2 lg:!ps-0 text-white bg-primary-700 lg:bg-transparent lg:text-primary-700 lg:dark:text-primary-700 dark:bg-primary-600 lg:dark:bg-transparent cursor-default"
	>
		<NavLi class="lg:mb-0 lg:px-2" href={base}>Home</NavLi>
	</NavUl>

	<div class="ms-auto flex items-center">
		<DarkMode size="lg" class="inline-block hover:text-gray-900 dark:hover:text-white" />
		<Tooltip class="dark:bg-gray-900" placement="bottom-end">Toggle dark mode</Tooltip>

		<Button color="primary" size="lg" class="ms-3" on:click={signOut}>Sign Out</Button>
	</div>
</Navbar>
