document.addEventListener("DOMContentLoaded", () => {
	const body = document.querySelector("body[data-bg]");
	if (body) {
		const imagem = body.dataset.bg;
		body.style.backgroundImage = `url("/static/img/galeria/${imagem}")`;
	}
});
