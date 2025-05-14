document.addEventListener("DOMContentLoaded", () => {
	// Injetar dinamicamente a imagem de fundo salva no config.json
	const body = document.querySelector("body.body-admin-dash");
	if (body && body.dataset.bg) {
		body.style.backgroundImage = `url("/static/img/galeria/${body.dataset.bg}")`;
	}

	const tabs = document.querySelectorAll(".tab");
	const abas = document.querySelectorAll(".aba");

	// Aleternância manual entre abas
	tabs.forEach((tab, index) => {
		tab.addEventListener("click", () => {
			tabs.forEach(t => t.classList.remove("active"));
			abas.forEach(a => a.classList.remove("active"));

			tab.classList.add("active");
			abas[index].classList.add("active");
		});
	});

	// Detecta query string ?aba=imagens para ativar essa aba
	const params = new URLSearchParams(window.location.search);
	const abaInicial = params.get("aba");

	if (abaInicial === "imagens") {
		tabs.forEach(t => t.classList.remove("active"));
		abas.forEach(a => a.classList.remove("active"));

		tabs[1].classList.add("active");
		abas[1].classList.add("active");
	}

	// Validação de tamanho para uload de imagens
	const MAX_FILE_SIZE_MB = 25;
	const formImagem = document.getElementById("form-upload-imagem");
	const inputImagem = document.getElementById("input-imagem");

	if (formImagem && inputImagem) {
		formImagem.addEventListener("submit", function (e) {
			const arquivos = inputImagem.files;

			for (let i = 0; i < arquivos.length; i++) {
				const arquivo = arquivos[i];
				const tamanhoMB = arquivo.size / (1024 * 10124);

				if (tamanhoMB > 25) {
					e.preventDefault();
					alert(`O arquivo "${arquivo.name}" tem ${tamanhoMB.toFixed(2)}MB e excede o limite de 25MB.`);
					return;
				}
			}
		});
	}

	// DRAG AND DROP DE MÚSICAS
	const dropArea = document.querySelector(".drop-area");
	const inputMusicas = document.getElementById("input-musicas");
	const formMusicas = document.getElementById("form-upload-musicas");

	if (dropArea && inputMusicas && formMusicas) {
		// Destaque visual ao arrastar
		dropArea.addEventListener("dragover", (e) => {
			e.preventDefault();
			dropArea.classList.add("dragover");
		});

		dropArea.addEventListener("dragleave", () => {
			dropArea.classList.remove("dragover");
		});

		// Soltou os arquivos na área
		dropArea.addEventListener("drop", (e) => {
			e.preventDefault();
			dropArea.classList.remove("dragover");

			const arquivos = DataTransfer.files;
			inputMusicas.files = arquivos;
			formMusicas.submit();
		});
	}

	const progressContainer = document.querySelector(".progress-container");
	const progressBar = document.getElementById("progress-bar");

	if (formMusicas && inputMusicas && progressContainer && progressBar) {
		formMusicas.addEventListener("submit", function (e) {
			e.preventDefault();

			const arquivos = inputMusicas.files;
			if (arquivos.length === 0) {
				alert("Selecione ao menos um arquivo.");
				return;
			}

			const formData = new FormData();
			for (let i = 0; i < arquivos.length; i++) {
				formData.append("musicas", arquivos[i]);
			}

			const xhr = new XMLHttpRequest();
			xhr.open("POST", "/upload-musicas", true);

			xhr.upload.addEventListener("progress", (event) => {
				if (event.lengthComputable) {
					const percent = (event.loaded / event.total) * 100;
					progressContainer.style.display = "block";
					progressBar.style.width = `${percent}%`;

					// Ativa o overlay após o upload
					if (percent >= 100) {
						document.querySelector(".processing-overlay").style.display = "flex";
					}
				}
			});

			xhr.onload = () => {
				if (xhr.status === 200) {
					window.location.href = "/admin-dashboard?aba=musicas";
				} else {
					alert("Erro ao enviar as músicas.");
				}
			};

			xhr.send(formData);
		});
	}

	// Seleção de músicas para exclusão
	const checkTodos = document.getElementById("check-todos");
	const checkboxes = document.querySelectorAll(".check-musica");
	const contadorSpan = document.getElementById("contador-selecionadas");

	if (checkTodos && checkboxes.length > 0 && contadorSpan) {
		checkTodos.addEventListener("change", () => {
			const marcado = checkTodos.checked;
			checkboxes.forEach(cb => cb.checked = marcado);
			atualizarContador();
		});

		checkboxes.forEach(cb => {
			cb.addEventListener("change", atualizarContador);
		});

		function atualizarContador() {
			const totalSelecionados = document.querySelectorAll(".check-musica:checked").length;
			if (totalSelecionados === 0) {
				contadorSpan.textContent = "Nenhuma música selecionada";
			} else {
				contadorSpan.textContent = `${totalSelecionados} músicas selecionadas`;
			}
		}
	}
});

