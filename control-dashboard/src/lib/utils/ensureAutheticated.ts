import { dev } from '$app/environment';
import { base } from '$app/paths';

export default async function isLoggedIn(fetchFunction) {
	const baseUrl = dev ? '/api' : '';

	let response = await fetchFunction(`${baseUrl}/admin/is-logged-in`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json'
		}
	});
	let responseJson = await response.json();
	if (responseJson.loggedIn) {
		return true;
	} else {
		return false;
	}
}
