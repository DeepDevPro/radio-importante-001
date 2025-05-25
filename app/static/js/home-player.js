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
		const atual = playlist[currentIndex];
		titulo.textContent = "🎵 Tocando agora";
		arquivo.textContent = `Arquivo: ${atual.split("/").pop()}`;
		modal.style.display = "flex";
	});

	modal.addEventListener("click", () => {
		modal.style.display = "none";
	});

	document.addEventListener("keydown", (event) => {
		if (event.key === "Escape") {
			modal.style.display = "none";
		}
	});

});

