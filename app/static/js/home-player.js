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

	// Se a função de baixo funcionar posso apagar essa, senão volto com ela;
	// function tocarAtual() {
	// 	audio.src = playlist[currentIndex];
	// 	audio.play();
	// 	playBtn.src = "/static/icons/pause.svg";
	// }

	function tocarAtual() {
		const atual = playlist[currentIndex];
		audio.src = atual;
		audio.play();
		playBtn.src = "/static/icons/pause.svg";

		// 🔤 Extrai nome legível da música
		const nomeArquivo = decodeURIComponent(atual.split("/").pop().replace(".mp3", ""));
		const nomeSemPrefixo = nomeArquivo.includes("_") ? nomeArquivo.split("_").slice(1).join("_") : nomeArquivo;

		let artista = "Desconhecido";
		let titulo = nomeSemPrefixo.replace(/_/g, " ").trim();

		if (nomeSemPrefixo.includes("-")) {
			const partes = nomeSemPrefixo.split("-");
			artista = partes[0].replace(/_/g, " ").trim();
			titulo = partes.slice(1).join("-").replace(/_/g, " ").trim();
		}


		// 🎵 Atualiza na tela
		document.getElementById("musica-nome").textContent = `${artista} "${titulo}"`;
		// document.getElementById("musica-nome").textContent = `${artista} - "${titulo}"`;


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

	infoBtn.addEventListener("click", (event) => {
		event.stopPropagation(); // Evita conflito com modal

		if (modal.style.display === "flex") {
			// 🔁 Se já está aberto, fecha
			modal.style.display = "none";
			return;
		}

		// 🎵 Atualiza as infos e abre
		const atual = playlist[currentIndex];
		const nomeArquivo = decodeURIComponent(atual.split("/").pop().replace(".mp3", ""));
		const nomeSemPrefixo = nomeArquivo.includes("_") ? nomeArquivo.split("_").slice(1).join("_") : nomeArquivo;

		let artista = "Artista Desconhecido";
		let titulo = "Faixa sem título";

		if (nomeSemPrefixo.includes("-")) {
			const partes = nomeSemPrefixo.split("-");
			artista = partes[0].replace(/_/g, " ").trim();
			titulo = partes.slice(1).join("-").replace(/_/g, " ").trim();
		} else {
			titulo = nomeSemPrefixo.replace(/_/g, " ").trim();
		}

		document.getElementById("info-artista").textContent = artista;
		document.getElementById("info-titulo").textContent = `"${titulo}"`;

		modal.style.display = "flex";
	});


	modal.addEventListener("click", (event) => {
		// Fecha o modal ao clicar em qualquer lugar, inclusive no conteúdo
		modal.style.display = "none";
	});
	
	document.addEventListener("keydown", (event) => {
		if (event.key === "Escape") {
			modal.style.display = "none";
		}
	});

	function pingServidor() {
		fetch("/ping", {
			method: "POST"
		}).then(response => {
			if (!response.ok) {
				console.error("Falha no ping do servidor");
			}
		}).catch(err => {
			console.error("Erro no ping:", err);
		});
	}

	// Inicia o ping a cada 60 segundos (60000 ms)
	setInterval(pingServidor, 60000);

	// E já manda o primeiro ping ao abrir
	pingServidor();

	
});

