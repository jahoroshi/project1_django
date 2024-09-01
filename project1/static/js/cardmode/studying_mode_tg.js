document.addEventListener('DOMContentLoaded', async function () {
    let mainCardsQueue = [];  // Основная переменная с карточками
    let preloadCardsQueue = [];  // Переменная для подгрузки новых карточек
    let currentCardIndex = 0;
    let minCardsThreshold;
    let config = {};
    let studyMode = '';
    let studyFormat = '';
    let soundUrlCache = null;
    let audio = null;
    let count = 0;
    let revealIndex = 0;
    let cardData = {};
    let ratings_count = {}

    const knownButton = document.getElementById('known-btn');
    const cardFront = document.getElementById('card-text');
    const cardBack = document.getElementById('card-back');
    const hintContainer = document.getElementById('hint-container');
    const similarWordsContainer = document.getElementById('similar-words-container');
    const lettersContainer = document.getElementById('letters-container');
    const resultContainer = document.getElementById('result-container');
    const actionButtons = document.querySelectorAll('#show-back-btn, #show-hint-btn, #show-similar-btn, #show-first-letters-btn, #scramble-letters-btn');

    async function initializeConfig() {
        const currentUrl = new URL(window.location.href);
        const slug = currentUrl.searchParams.get('slug');
        studyMode = currentUrl.searchParams.get('mode');
        studyFormat = currentUrl.searchParams.get('format') || 'text';
        const configUrl = `/api/v1/study/get_start_config/${slug}/${studyMode}/${studyFormat}/`;

        console.log('Запрос конфигурации:', configUrl);

        try {
            const response = await fetch(configUrl);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            config = await response.json();
            console.log('Конфигурация получена:', config);
            return config;
        } catch (error) {
            console.error('Ошибка при получении конфигурации:', error);
            return null;
        }
    }

     function hideButtons() {
        const buttonsToShow = config.buttons_to_show;
        console.log(buttonsToShow)

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



    async function fetchCards() {
        console.log('Запрос карточек по URL:', config.urls.card_process);

        try {
            const response = await fetch(config.urls.card_process);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            ratings_count = data.ratings_count
            preloadCardsQueue.push(...data.cards);
            console.log('Карточки подгружены:', data.cards);
        } catch (error) {
            console.error('Ошибка при подгрузке карточек:', error);
        }
    }

    function updateMinCardsThreshold() {
        minCardsThreshold = Math.ceil(mainCardsQueue.length * 0.2); // 20% от текущего числа карточек
        console.log('Обновленное minCardsThreshold:', minCardsThreshold);
    }

    const configData = await initializeConfig();
    if (configData) {
        await fetchCards();  // Загружаем первую партию карточек в подгрузочную переменную
       hideButtons();
        switchToPreloadQueue();  // Переключаемся на подгрузочную переменную
        loadCard();  // Загружаем первую карточку
    }

    function switchToPreloadQueue() {
        mainCardsQueue = [...preloadCardsQueue];  // Переносим данные из подгрузочной переменной в основную
        preloadCardsQueue = [];  // Очищаем подгрузочную переменную
        currentCardIndex = 0;  // Сбрасываем индекс текущей карточки
        updateMinCardsThreshold();  // Обновляем minCardsThreshold
        console.log('Переключение на подгруженные карточки. Обновлено mainCardsQueue:', mainCardsQueue);
    }

    function loadCard() {
        console.log('Загрузка карточки:', currentCardIndex);

        if (currentCardIndex >= mainCardsQueue.length) {
            if (preloadCardsQueue.length > 0) {
                switchToPreloadQueue();
            } else {
                console.warn('Все карточки закончились');
                document.getElementById('no-cards-message').classList.remove('hidden');
                return;
            }
        }

        cardData = mainCardsQueue[currentCardIndex];
        console.log('Текущая карточка:', cardData);

        if (!cardData.card__side1) {
            console.warn('Пустая карточка. Завершение сеанса.');
            document.getElementById('hidden-container').classList.add('hidden');
            document.getElementById('show-container-message').classList.remove('hidden');
            document.getElementById('show-container-trophy').classList.remove('hidden');
            return;
        }

        if (config.study_format === 'audio') {
            cardFront.innerText = 'Play';
        } else {
            cardFront.innerText = cardData.card__side1;
        }

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

        showKnownButton(cardData);


        if (mainCardsQueue.length - currentCardIndex <= minCardsThreshold && preloadCardsQueue.length === 0) {
            console.log('Осталось мало карточек. Запрос новой партии.');
            fetchCards();
        }
    }
    console.log('study_mode  ', studyMode)
    function showKnownButton(cardData) {
        if (cardData) {
            knownButton.classList.add('hidden');
            if (!cardData.easiness && studyMode === 'new') {
                knownButton.classList.remove('hidden');
            }
        }
    }

    document.querySelectorAll('.rating-button').forEach(button => {
        button.addEventListener('click', function () {
            const rating = parseInt(this.getAttribute('data-rating'));
            const cardData = mainCardsQueue[currentCardIndex];
            console.log(`Оценка карточки: ${cardData.id}, Рейтинг: ${rating}`);

            fetch(config.urls.card_process, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': config.csrf_token
                },
                body: JSON.stringify({rating: rating, mappings_id: cardData.id})
            }).then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                console.log('Оценка отправлена успешно');
            }).catch(error => console.error('Ошибка при отправке рейтинга:', error));

            currentCardIndex++;
            loadCard();
        });
    });

    // Вызов функции для первой карточки
    loadCard();



  // const updateCounters = (ratings) => {
  //       document.getElementById('again-count').innerText = ratings[1] || 0;
  //       document.getElementById('hard-count').innerText = ratings[2] || 0;
  //       document.getElementById('good-count').innerText = ratings[3] || 0;
  //   };
  //
  //   document.getElementById('easy-btn').addEventListener('click', function () {
  //       count++;
  //       document.getElementById('easy-count').innerText = count;
  //   });


    console.log('card_data:  ', cardData.card__side1, cardData)
    const showBackButton = document.getElementById('show-back-btn');
    if (showBackButton) {
        showBackButton.addEventListener('click', function () {
            if (studyFormat === 'audio') {
                cardFront.innerText = cardData.card__side1;
            }
            cardBack.innerText = cardData.card__side2;
            cardBack.classList.remove('hidden');
            makeButtonsInactive();
        });
    }

    const showHintButton = document.getElementById('show-hint-btn');
    if (showHintButton) {
        showHintButton.addEventListener('click', function () {
            const hintUrl = config.urls.get_hint.replace('dummy_mappings_id', cardData.id);
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
            const similarWordsUrl = config.urls.get_similar_words.replace('dummy_mappings_id', cardData.id);
            fetch(similarWordsUrl).then(response => response.json()).then(data => {
                similarWordsContainer.innerHTML = '';
                            console.log('data   ', data)

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
        const sentence = cardData.card__side2;
        const words = sentence.split(' ');

        if (words.length < 3) {
            revealIndex += 2;
            if (revealIndex > sentence.length) revealIndex = sentence.length;
            const revealed = sentence.slice(0, revealIndex);
            cardBack.innerText = revealed + '*'.repeat(sentence.length - revealIndex);
            if (revealIndex >= sentence.length) {
                makeButtonsInactive();
                revealIndex = 0;
            }
        } else {
            const revealWords = words.map((word, index) => {
                const revealChars = Math.min(revealIndex * 2, word.length);
                return word.slice(0, revealChars) + '*'.repeat(word.length - revealChars);
            });

            const revealedSentence = revealWords.join(' ');
            cardBack.innerText = revealedSentence;

            revealIndex += 1;
            if (revealIndex > Math.max(...words.map(word => Math.ceil(word.length / 2)))) {
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
        handleScrambleLettersClick();
    });
    scrambleLettersButton.addEventListener('touchstart', function () {
        handleScrambleLettersClick();
    });
}

function handleScrambleLettersClick() {
    disableOtherActionButtons(scrambleLettersButton.id);
    lettersContainer.innerHTML = '';
    const input = cardData.card__side2.trim();
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

    elements.forEach((element, index) => {
        const span = document.createElement('span');
        span.className = 'letter';
        span.innerText = element;

        const handleClick = () => {
            const currentIndex = isSentence ? userInput.length : userInput.length;
            const originalElement = isSentence ? words[currentIndex] : input[currentIndex];

            if (element === originalElement) {
                if (isSentence) {
                    userInput.push(element);
                    resultContainer.innerText = userInput.join(' ') + ' ';
                } else {
                    userInput += element;
                    resultContainer.innerText = userInput;
                }

                // Применяем изменения немедленно
                span.classList.add('inactive');

                // Отложенное выполнение проверки и оставшихся действий
                setTimeout(() => {
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
                }, 0);
            } else {
                span.classList.add('wrong-letter');
                setTimeout(() => {
                    span.classList.remove('wrong-letter');
                }, 1000);
            }
        };

        // Добавляем обработчики для событий click и touchstart
        span.addEventListener('click', handleClick);
        span.addEventListener('touchstart', handleClick);

        lettersContainer.appendChild(span);
    });
    lettersContainer.classList.remove('hidden');
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

    const playSoundButton = document.getElementById('card-front');
    playSoundButton.addEventListener('click', function () {
        if (!soundUrlCache) {
            const soundUrl = config.urls.get_sound.replace('dummy_mappings_id', cardData.id);
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
