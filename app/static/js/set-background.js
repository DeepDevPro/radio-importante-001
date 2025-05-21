document.addEventListener("DOMContentLoaded", () => {
	const body = document.querySelector("body[data-bg]");
	if (body) {
		const imagem = body.dataset.bg;
		const url = `https://radioimportante-uploads.s3.amazonaws.com/static/img/galeria/${imagem}`;
		body.style.backgroundImage = `url("${url}")`;
	}
});

// document.addEventListener("DOMContentLoaded", () => {
// 	const body = document.querySelector("body[data-bg]");
// 	if (body) {
// 		const imagem = body.dataset.bg;
// 		body.style.backgroundImage = `url("/static/img/galeria/${imagem}")`;
// 	}
// });