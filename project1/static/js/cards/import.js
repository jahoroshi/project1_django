document.addEventListener('DOMContentLoaded', function () {
            var customOptionInput1 = document.getElementById('id_words_separator_custom');
            var customOptionInput2 = document.getElementById('id_cards_separator_custom');
            var customRadio1 = document.getElementById('id_words_separator_2');
            var customRadio2 = document.getElementById('id_cards_separator_2');
            var textInput = document.getElementById('id_text');
            var previewContainer = document.getElementById('preview');
            var previewContainerWrapper = document.getElementById('preview-container');
            var cardCountElement = document.getElementById('card-count');

            // Вставка табуляции в текстовое поле
            textInput.addEventListener('keydown', function (e) {
                if (e.key === 'Tab') {
                    e.preventDefault();
                    var start = this.selectionStart;
                    var end = this.selectionEnd;
                    this.value = this.value.substring(0, start) + '\t' + this.value.substring(end);
                    this.selectionStart = this.selectionEnd = start + 1;
                    updatePreview();
                }
            });

            function escapeHTML(str) {
                return str.replace(/[&<>"']/g, function (match) {
                    switch (match) {
                        case '&':
                            return '&amp;';
                        case '<':
                            return '&lt;';
                        case '>':
                            return '&gt;';
                        case '"':
                            return '&quot;';
                        case "'":
                            return '&#39;';
                    }
                });
            }

            function updatePreview() {
                var text = textInput.value;
                var wordsSeparator = document.querySelector('input[name="words_separator"]:checked').value;
                var cardsSeparator = document.querySelector('input[name="cards_separator"]:checked').value;
                var wordsSeparatorCustom = customOptionInput1.value;
                var cardsSeparatorCustom = customOptionInput2.value;

                // Показываем или скрываем контейнер превью в зависимости от наличия текста
                if (!text.trim()) {
                    previewContainerWrapper.style.display = 'none';
                    cardCountElement.textContent = 'Cards: 0';
                    return;
                } else {
                    previewContainerWrapper.style.display = 'block';
                }

                // Определяем разделители
                var wordsSeparatorValue = (wordsSeparator === 'words_custom' && wordsSeparatorCustom) ? wordsSeparatorCustom : (wordsSeparator === 'tab' ? '\t' : (wordsSeparator === 'comma' ? ',' : null));
                var cardsSeparatorValue = (cardsSeparator === 'cards_custom' && cardsSeparatorCustom) ? cardsSeparatorCustom : (cardsSeparator === 'new_line' ? '\n' : (cardsSeparator === 'semicolon' ? ';' : null));

                // Проверка пользовательских разделителей
                if ((wordsSeparator === 'words_custom' && !wordsSeparatorCustom) || (cardsSeparator === 'cards_custom' && !cardsSeparatorCustom)) {
                    previewContainer.textContent = "Please enter custom separators.";
                    return;
                }

                // Разделяем текст на карточки и слова
                var cards = text.split(cardsSeparatorValue).filter(card => card.trim() !== '');
                previewContainer.innerHTML = ''; // Очищаем контейнер перед добавлением новых карточек

                cards.forEach(card => {
                    var cardElement = document.createElement('div');
                    cardElement.className = 'card';

                    var words = card.split(wordsSeparatorValue);
                    var formattedText = words.map(word => escapeHTML(word.trim())).join('<br>');

                    cardElement.innerHTML = formattedText;
                    previewContainer.appendChild(cardElement);
                });

                // Обновляем счетчик карточек
                cardCountElement.textContent = 'Cards: ' + cards.length;
            }

            customOptionInput1.addEventListener('focus', function () {
                customRadio1.checked = true;
            });

            customOptionInput2.addEventListener('focus', function () {
                customRadio2.checked = true;
            });

            textInput.addEventListener('input', updatePreview);
            document.querySelectorAll('input[name="words_separator"]').forEach(function (radio) {
                radio.addEventListener('change', updatePreview);
            });
            document.querySelectorAll('input[name="cards_separator"]').forEach(function (radio) {
                radio.addEventListener('change', updatePreview);
            });
            customOptionInput1.addEventListener('input', updatePreview);
            customOptionInput2.addEventListener('input', updatePreview);

            // Инициализируем предварительный просмотр при загрузке страницы
            updatePreview();
        });