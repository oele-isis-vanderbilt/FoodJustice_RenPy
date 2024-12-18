<script lang="ts">
	import { Button, Checkbox, Label, Input } from 'flowbite-svelte';
	import Footer from '$lib/components/footer.svelte';
	import { goto } from '$app/navigation';
	import { dev } from '$app/environment';
	import { base } from '$app/paths';

	let pending = $state(false);

	function onsubmit(event: SubmitEvent) {
		event.preventDefault();
		const form = event.target as HTMLFormElement;
		const data = new FormData(form);
		const body = Object.fromEntries(data.entries());
		pending = true;
		const baseUrl = dev ? '/api' : '';
		fetch(`${baseUrl}/admin/login`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(body)
		}).then(async (response) => {
			if (response.ok) {
				console.log(base || '/');
				pending = false;
				goto(base || '/');
			} else {
				pending = false;
				alert('Login failed\n' + (await response.text()));
			}
		}).catch((error) => {
			pending = false;
			alert('Login failed\n' + error);
		});
	}
</script>

<div class="flex items-center justify-center p-6 sm:p-8 md:p-12">
	<form class="flex w-full max-w-sm flex-col space-y-6" {onsubmit}>
		<h3 class="text-xl font-medium text-gray-900 dark:text-white">Sign In</h3>
		<Label class="space-y-2">
			<span>Username</span>
			<Input type="text" name="username" placeholder="username" required class="bg-gray-100 dark:bg-gray-700 dark:text"/>
		</Label>
		<Label class="space-y-2">
			<span>Your password</span>
			<Input type="password" name="password" placeholder="•••••" required />
		</Label>
		<Button type="submit" disabled={pending} class="w-full bg-red-800">Sign in</Button>
	</form>
</div>
<Footer />
