import isLoggedIn from '$lib/utils/ensureAutheticated';
import { redirect } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
	const hasLoggedIn = await isLoggedIn(fetch);
	if (hasLoggedIn) {
		redirect(302, '/');
	}
};
