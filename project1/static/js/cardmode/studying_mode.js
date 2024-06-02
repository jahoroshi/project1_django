document.addEventListener('DOMContentLoaded', function () {
    const config = JSON.parse(document.getElementById('context-json').textContent);
    const csrfToken = config.csrf_token;
    const slug = config.slug;
    const studyMode = config.study_mode;
    const urls = config.urls;

    const cardFront = document.getElementById('card-front');
    const cardBack = document.getElementById('card-back');
    const hintContainer = document.getElementById('hint-container');
    const similarWordsContainer = document.getElementById('similar-words-container');
    const lettersContainer = document.getElementById('letters-container');
    const resultContainer = document.getElementById('result-container');
    const actionButtons = document.querySelectorAll('#show-back-btn, #show-hint-btn, #show-similar-btn, #show-first-letters-btn, #scramble-letters-btn');
    let cardData = null;
    let soundUrlCache = null; // Кэш для URL звукового файла
    let audio = null;

    const loadCard = (data = null) => {
        if (data) {
            cardData = data;
            cardFront.innerText = data.front_side;
            cardBack.classList.add('hidden');
            cardBack.innerText = '';
            hintContainer.classList.add('hidden');
            similarWordsContainer.classList.add('hidden');
            lettersContainer.classList.add('hidden');
            resultContainer.innerText = '';
            resultContainer.classList.remove('correct-word');
            actionButtons.forEach(button => button.disabled = false);
            soundUrlCache = null;
            audio = null;
            similarWordsContainer.innerHTML = '';
            lettersContainer.innerHTML = '';
        } else {
            const url = `${urls.get_card}?study_mode=${studyMode}`;
            fetch(url).then(response => response.json()).then(data => {
                cardData = data;
                loadCard(data);
            });
        }
    };

    loadCard();

    const showBackButton = document.getElementById('show-back-btn');
    if (showBackButton) {
        showBackButton.addEventListener('click', function () {
            cardBack.innerText = cardData.back_side;
            cardBack.classList.remove('hidden');
            makeButtonsInactive();
        });
    }

    const showHintButton = document.getElementById('show-hint-btn');
    if (showHintButton) {
        showHintButton.addEventListener('click', function () {
            const hintUrl = urls.get_hint.replace('dummy_mappings_id', cardData.mappings_id);
            fetch(hintUrl).then(response => response.json()).then(data => {
                hintContainer.innerText = data.hint;
                hintContainer.classList.remove('hidden');
            });
        });
    }

    const showSimilarButton = document.getElementById('show-similar-btn');
    if (showSimilarButton) {
        showSimilarButton.addEventListener('click', function () {
            disableOtherActionButtons(this.id);
            const similarWordsUrl = urls.get_similar_words.replace('dummy_mappings_id', cardData.mappings_id);
            fetch(similarWordsUrl).then(response => response.json()).then(data => {
                similarWordsContainer.innerHTML = '';
                data.similar_words.forEach(word => {
                    const button = document.createElement('button');
                    button.innerText = word;
                    button.addEventListener('click', function () {
                        if (word === data.back_side) {
                            resultContainer.innerText = 'Correct!';
                            resultContainer.classList.add('correct-word');
                        } else {
                            resultContainer.innerText = `Wrong! The correct word is ${data.back_side}`;
                        }
                        makeButtonsInactive();
                        disableSimilarWordButtons();
                    });
                    similarWordsContainer.appendChild(button);
                });
                similarWordsContainer.classList.remove('hidden');
            });
        });
    }

    function disableSimilarWordButtons() {
        const buttons = similarWordsContainer.querySelectorAll('button');
        buttons.forEach(button => {
            button.disabled = true;
        });
    }

    let revealIndex = 0;

    const showFirstLettersButton = document.getElementById('show-first-letters-btn');
    if (showFirstLettersButton) {
        showFirstLettersButton.addEventListener('click', function () {
            disableOtherActionButtons(this.id);
            const sentence = cardData.back_side;
            const words = sentence.split(' ');

            if (words.length < 3) {
                // Слово состоит из одной части
                revealIndex += 2;
                if (revealIndex > sentence.length) revealIndex = sentence.length;
                const revealed = sentence.slice(0, revealIndex);
                cardBack.innerText = revealed + '*'.repeat(sentence.length - revealIndex);
                if (revealIndex >= sentence.length) {
                    makeButtonsInactive();
                    revealIndex = 0;
                }

            } else {
                // Слово состоит из нескольких частей
                revealIndex += 1;
                if (revealIndex > words.length) revealIndex = words.length;
                const revealed = words.slice(0, revealIndex).join(' ');
                const remainingWords = words.slice(revealIndex).join(' ');
                cardBack.innerText = revealed + ' ' + '*'.repeat(remainingWords.length);
                if (revealIndex >= sentence.length) {
                    makeButtonsInactive();
                    revealIndex = 0;
                }
            }

            cardBack.classList.remove('hidden');
        });
    }

    function shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
    }

    const scrambleLettersButton = document.getElementById('scramble-letters-btn');
    if (scrambleLettersButton) {
        scrambleLettersButton.addEventListener('click', function () {
            disableOtherActionButtons(this.id);
            lettersContainer.innerHTML = '';
            const input = cardData.back_side.trim();
            const words = input.split(' ');
            const isSentence = words.length > 2; // проверка, является ли это предложение (более 2 слов)
            let elements;

            if (isSentence) {
                elements = words.slice(); // используем копию массива слов
            } else {
                elements = input.split(''); // используем буквы
            }

            shuffleArray(elements);
            let userInput = isSentence ? [] : ''; // массив для предложений, строка для слов

            elements.forEach(element => {
                const span = document.createElement('span');
                span.className = 'letter';
                span.innerText = element;
                span.addEventListener('click', () => {
                    const currentIndex = userInput.length;
                    const originalElement = isSentence ? words[currentIndex] : input[currentIndex];

                    if (element === originalElement) {
                        if (isSentence) {
                            userInput.push(element);
                            resultContainer.innerText = userInput.join(' ') + ' ';
                        } else {
                            userInput += element;
                            resultContainer.innerText = userInput;
                        }
                        span.classList.add('inactive');

                        // Проверка полного соответствия ввода
                        if ((isSentence && userInput.join(' ') === input) || (!isSentence && userInput === input)) {
                            resultContainer.innerText = `${isSentence ? userInput.join(' ') : userInput} - Correct!`;
                            resultContainer.classList.add('correct-word');
                            lettersContainer.classList.add('hidden');
                            makeButtonsInactive();
                        }
                    } else {
                        span.classList.add('wrong-letter');
                        setTimeout(() => {
                            span.classList.remove('wrong-letter');
                        }, 1000);
                    }
                });
                lettersContainer.appendChild(span);
            });
            lettersContainer.classList.remove('hidden');
        });
    }

    function disableOtherActionButtons(activeButtonId) {
        actionButtons.forEach(button => {
            if (button.id !== activeButtonId) {
                button.disabled = true;
            }
        });
    }

    function makeButtonsInactive() {
        actionButtons.forEach(button => button.disabled = true);
    }

    document.querySelectorAll('.rating-button').forEach(button => {
        button.addEventListener('click', function () {
            const rating = parseInt(this.getAttribute('data-rating'));
            fetch(urls.get_card, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({rating: rating, mappings_id: cardData.mappings_id})
            })
                .then(response => response.json())
                .then(data => {
                    loadCard(data);
                });
        });
    });

    const playSoundButton = document.getElementById('play-sound-btn');
    playSoundButton.addEventListener('click', function () {
        if (!soundUrlCache) {
            const soundUrl = urls.get_sound.replace('dummy_mappings_id', cardData.mappings_id);
            fetch(soundUrl)
                .then(response => response.blob())
                .then(blob => {
                    soundUrlCache = URL.createObjectURL(blob);
                    audio = new Audio(soundUrlCache);
                    audio.play();
                });
        } else {
            audio.play();
        }
    });
});
