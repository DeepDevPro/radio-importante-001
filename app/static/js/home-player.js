document.addEventListener("DOMContentLoaded", () => {
	const audio = document.getElementById('player');
	const playBtn = document.getElementById("play-btn");
	const nextBtn = document.getElementById("next-btn");
	const infoBtn = document.getElementById("info-btn");
	const modal = document.getElementById("info-modal");
	const fecharBtn = document.getElementById("fechar-info");
	const titulo = document.getElementById("info-titulo");
	const arquivo = document.getElementById("info-arquivo");

	const playlist = window.playlist;
	let currentIndex = 0;

	if (!window.playlist || window.playlist.length === 0) {
		console.warn("Nenhuma música disponível na playlist.");
		return;
	}

	function tocarAtual() {
		audio.src = playlist[currentIndex];
		audio.play();
		playBtn.src = "/static/icons/pause.svg";
	}

	playBtn.addEventListener("click", () => {
		if (audio.paused) {
			tocarAtual();
		} else {
			audio.pause();
			playBtn.src = "/static/icons/play.svg";
		}
	});

	function avancar() {
		currentIndex++;

		// 🔁 Se chegou ao fim, reembaralha no frontend
		if (currentIndex >= playlist.length) {
			console.log("🔀 Fim da fila, reembaralhando...");
			playlist.sort(() => Math.random() - 0.5);
			currentIndex = 0;
		}

		tocarAtual();
	}

	nextBtn.addEventListener("click", avancar);
	audio.addEventListener("ended", avancar);

	// 🔍 Info Modal
	infoBtn.addEventListener("click", () => {
		const src = playlist[currentIndex];
		const nomeArquivo = decodeURIComponent(src.split("/").pop().replace(".mp3", ""));
		let artista = "Artista Desconhecido";
		let tituloFormatado = "Faixa sem título";
	
		if (nomeArquivo.includes("-")) {
			const partes = nomeArquivo.split("-");
			artista = partes[0].trim();
			tituloFormatado = partes.slice(1).join("-").replace(/_/g, " ").trim();
		} else {
			tituloFormatado = nomeArquivo.replace(/_/g, " ");
		}
	
		document.getElementById("info-artista").textContent = artista;
		document.getElementById("info-titulo").textContent = `"${tituloFormatado}"`;
		modal.style.display = "flex";
	});
	
});
