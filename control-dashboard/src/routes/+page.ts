import type { PageLoad } from './$types';
import isLoggedIn from '$lib/utils/ensureAutheticated';
import { redirect } from '@sveltejs/kit';
import type { SyncFlowSettings } from '$lib/components/syncflow-settings.svelte';
import { base } from '$app/paths';
import { dev } from '$app/environment';

export const load: PageLoad = async ({ params, fetch }) => {
	let loggedIn = await isLoggedIn(fetch);

	if (!loggedIn) {
		redirect(302, base + '/login');
	} else {
		const baseUrl = dev ? '/api' : '';
		let response = await fetch(`${baseUrl}/syncflow/runtime-settings`, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (response.ok) {
			let responseJson: SyncFlowSettings = await response.json();
			return {
				settings: responseJson
			};
		} else {
			return {
				status: response.status,
				error: response.statusText
			};
		}
	}
};
