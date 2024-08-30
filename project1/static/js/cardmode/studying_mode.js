document.addEventListener('DOMContentLoaded', async function () {
    async function initializeConfig() {
        try {
            const currentUrl = new URL(window.location.href);

            const slug = currentUrl.searchParams.get('slug');

            const studyMode = currentUrl.searchParams.get('mode');

            const studyFormat = currentUrl.searchParams.get('format') || 'text';

            const configUrl = `/api/v1/study/get_start_config/${slug}/${studyMode}/${studyFormat}/`;

            const response = await fetch(configUrl);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Ошибка при получении конфигурации:', error);
            return null;
        }
    }


    const config = await initializeConfig();
    const studyFormat = config.study_format;
    const csrfToken = config.csrf_token;
    const urls = config.urls;
    const getUrl = urls.get_card;
    const knownButton = document.getElementById('known-btn');
    const cardFront = document.getElementById('card-text');
    const cardBack = document.getElementById('card-back');
    const hintContainer = document.getElementById('hint-container');
    const similarWordsContainer = document.getElementById('similar-words-container');
    const lettersContainer = document.getElementById('letters-container');
    const resultContainer = document.getElementById('result-container');
    const actionButtons = document.querySelectorAll('#show-back-btn, #show-hint-btn, #show-similar-btn, #show-first-letters-btn, #scramble-letters-btn');

    let cardData = null;
    let soundUrlCache = null;
    let audio = null;
    let count = 0;
    let revealIndex = 0;


    function hideButtons() {
        const buttonsToShow = config.buttons_to_show;

        const buttonIds = {
            show_back: 'show-back-btn',
            show_hint: 'show-hint-btn',
            show_similar: 'show-similar-btn',
            show_first_letters: 'show-first-letters-btn',
            scramble_letters: 'scramble-letters-btn',
            speech: 'speech-btn'
        };

        for (const [key, value] of Object.entries(buttonIds)) {
            const button = document.getElementById(value);
            if (button && buttonsToShow[key]) {
                button.classList.remove('hidden');
            }
        }
    }

    hideButtons();

    const loadCard = (data = null) => {
        if (data) {
            cardData = data;
            console.log(cardData)
            if (!data.front_side) {
                console.log(data.front_side)
                document.getElementById('hidden-container').classList.add('hidden');
                document.getElementById('show-container-message').classList.remove('hidden');
                document.getElementById('show-container-trophy').classList.remove('hidden');

                setTimeout(() => {
                    window.location.href = "/";
                }, 3000);
                return;
            }
            if (studyFormat === 'audio') {
                cardFront.innerText = 'Play';
            } else {
                cardFront.innerText = data.front_side;
            }
            // cardFront.innerText = data.front_side;
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
            revealIndex = 0;
            similarWordsContainer.innerHTML = '';
            lettersContainer.innerHTML = '';
            showKnownButton();
            updateCounters(cardData.ratings_count);
        } else {
            fetch(getUrl).then(response => response.json()).then(data => {
                cardData = data;
                updateCounters(cardData.ratings_count);

                loadCard(data);
            });
        }
    };

    const hideElements = () => {
        const hiddenContainer = document.getElementById('hidden-container').classList.add('hidden');
        const showMessage = document.getElementById('show-container-message').classList.remove('hidden');
        const showTrophy = document.getElementById('show-container-trophy').classList.remove('hidden');
        hiddenContainer.classList.add('hidden');
        showMessage.classList.remove('hidden');
        showTrophy.classList.remove('hidden');
    };

    const showKnownButton = () => {
        if (cardData) {
            knownButton.classList.add('hidden');
            if (cardData.ratings_count.hasOwnProperty(5)) {
                knownButton.classList.remove('hidden')
            }
        }
    };

    const updateCounters = (ratings) => {
        document.getElementById('again-count').innerText = ratings[1] || 0;
        document.getElementById('hard-count').innerText = ratings[2] || 0;
        document.getElementById('good-count').innerText = ratings[3] || 0;
    };

    document.getElementById('easy-btn').addEventListener('click', function () {
        count++;
        document.getElementById('easy-count').innerText = count;
    });

    loadCard();


    const showBackButton = document.getElementById('show-back-btn');
    if (showBackButton) {
        showBackButton.addEventListener('click', function () {
            if (studyFormat === 'audio') {
                cardFront.innerText = cardData.front_side;
            }
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
                hintContainer.innerText = data;
                hintContainer.classList.remove('hidden');
                disableOtherActionButtons(showBackButton.id);


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
                    button.className = 'list-group-item list-group-item-action similar-words';
                    button.setAttribute('type', 'button');
                    button.innerText = word;
                    button.addEventListener('click', function () {
                        if (word === data.back_side) {
                            button.classList.add('correct-choice'); // Добавление стиля для правильного ответа
                        } else {
                            button.classList.add('wrong-choice'); // Добавление стиля для ошибочного ответа
                            const correctButton = Array.from(similarWordsContainer.querySelectorAll('button')).find(btn => btn.innerText === data.back_side);
                            if (correctButton) {
                                correctButton.classList.add('correct-choice'); // Добавление стиля для правильного ответа
                            }
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
                cardBack.innerText = revealed + ' ' + '* '.repeat(remainingWords.length);
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
                            resultContainer.innerHTML = `${isSentence ? userInput.join(' ') : userInput} <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="currentColor" class="bi bi-check2-all" viewBox="0 0 16 16">
                              <path d="M12.354 4.354a.5.5 0 0 0-.708-.708L5 10.293 1.854 7.146a.5.5 0 1 0-.708.708l3.5 3.5a.5.5 0 0 0 .708 0l7-7zm-4.208 7-.896-.897.707-.707.543.543 6.646-6.647a.5.5 0 0 1 .708.708l-7 7a.5.5 0 0 1-.708 0z"/>
                              <path d="m5.354 7.146.896.897-.707.707-.897-.896a.5.5 0 1 1 .708-.708"/>
                            </svg>`;


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
            fetch(getUrl, {
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

    const playSoundButton = document.getElementById('card-front');
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
