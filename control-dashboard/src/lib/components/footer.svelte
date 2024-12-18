<script lang="ts">
	import { Footer, FooterCopyright } from 'flowbite-svelte';
	let logo = '/logo.png';
</script>

<Footer class="fixed bottom-0 w-full bg-white dark:bg-gray-900">
	<div class="max-w-8xl mx-auto flex flex-col py-6 lg:py-6">
		<div class="flex items-center justify-center px-4 text-center">
			<FooterCopyright
				href="https://engageai.org/"
				target="_blank"
				by="EngageAI Institute"
				copyrightMessage=" | All Rights Reserved."
			/>
		</div>
	</div>
</Footer>
