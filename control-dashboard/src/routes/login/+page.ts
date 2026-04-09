import isLoggedIn from '$lib/utils/ensureAutheticated';
import { redirect } from '@sveltejs/kit';
import { base } from '$app/paths';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
	const hasLoggedIn = await isLoggedIn(fetch);
	if (hasLoggedIn) {
		throw redirect(302, base || '/');
	}
};
