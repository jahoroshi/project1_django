document.addEventListener('DOMContentLoaded', async function () {
    // Arrays to hold the main cards and preload new ones
    let mainCardsQueue = [];  // Primary array holding the cards
    let preloadCardsQueue = [];  // Array for preloading new cards
    let currentCardIndex = 0;  // Index to track the current card
    let minCardsThreshold;  // Threshold to determine when to load more cards
    let config = {};  // Configuration object fetched from the server
    let studyMode = '';  // Study mode, e.g., 'new', 'review'
    let studyFormat = '';  // Study format, e.g., 'text', 'audio'
    let soundUrlCache = null;  // Cache for sound URLs to avoid refetching
    let audio = null;  // Audio object to play sounds
    let count = 0;  // Counter for various purposes
    let revealIndex = 0;  // Index to track the revealed portion of the answer
    let cardData = {};  // Current card data
    let ratings_count = {};  // Object to hold ratings count

    // Elements from the DOM
    const knownButton = document.getElementById('known-btn');
    const cardFront = document.getElementById('card-text');
    const cardBack = document.getElementById('card-back');
    const hintContainer = document.getElementById('hint-container');
    const similarWordsContainer = document.getElementById('similar-words-container');
    const lettersContainer = document.getElementById('letters-container');
    const resultContainer = document.getElementById('result-container');
    const actionButtons = document.querySelectorAll('#show-back-btn, #show-hint-btn, #show-similar-btn, #show-first-letters-btn, #scramble-letters-btn');

    // Function to fetch configuration data from the server
    async function initializeConfig() {
        const currentUrl = new URL(window.location.href);
        const slug = currentUrl.searchParams.get('slug');
        studyMode = currentUrl.searchParams.get('mode');
        studyFormat = currentUrl.searchParams.get('format') || 'text';
        const configUrl = `/api/v1/study/get_start_config/${slug}/${studyMode}/${studyFormat}/`;

        console.log('Requesting configuration:', configUrl);

        try {
            const response = await fetch(configUrl);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            config = await response.json();
            console.log('Configuration received:', config);
            return config;
        } catch (error) {
            console.error('Error fetching configuration:', error);
            return null;
        }
    }

    // Function to hide or show buttons based on the configuration
    function hideButtons() {
        const buttonsToShow = config.buttons_to_show;
        console.log(buttonsToShow);

        const buttonIds = {
            show_back: 'show-back-btn',
            show_hint: 'show-hint-btn',
            show_similar: 'show-similar-btn',
            show_first_letters: 'show-first-letters-btn',
            scramble_letters: 'scramble-letters-btn',
            speech: 'speech-btn'
        };

        // Loop through each button and hide/show it based on config
        for (const [key, value] of Object.entries(buttonIds)) {
            const button = document.getElementById(value);
            if (button && buttonsToShow[key]) {
                button.classList.remove('hidden');
            }
        }
    }

    // Function to fetch cards from the server and populate the preload queue
    async function fetchCards() {
        console.log('Requesting cards from URL:', config.urls.card_process);

        try {
            const response = await fetch(config.urls.card_process);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            ratings_count = data.ratings_count;
            preloadCardsQueue.push(...data.cards);
            console.log('Cards preloaded:', data.cards);
        } catch (error) {
            console.error('Error fetching cards:', error);
        }
    }

    // Function to update the minimum threshold for triggering card loading
    function updateMinCardsThreshold() {
        minCardsThreshold = Math.ceil(mainCardsQueue.length * 0.2); // 20% of current cards
        console.log('Updated minCardsThreshold:', minCardsThreshold);
    }

    // Initialize configuration and load the first set of cards
    const configData = await initializeConfig();
    if (configData) {
        await fetchCards();  // Load the first batch of cards into the preload queue
        hideButtons();
        switchToPreloadQueue();  // Switch from preload to main queue
        loadCard();  // Load the first card
    }

    // Function to switch from preload queue to main queue
    function switchToPreloadQueue() {
        mainCardsQueue = [...preloadCardsQueue];  // Move cards to main queue
        preloadCardsQueue = [];  // Clear preload queue
        currentCardIndex = 0;  // Reset current card index
        updateMinCardsThreshold();  // Update threshold for loading more cards
        console.log('Switched to preloaded cards. Updated mainCardsQueue:', mainCardsQueue);
    }

    // Function to load the current card data
    function loadCard() {
        console.log('Loading card:', currentCardIndex);

        // Check if we've reached the end of the current card queue
        if (currentCardIndex >= mainCardsQueue.length) {
            if (preloadCardsQueue.length > 0) {
                switchToPreloadQueue();  // Switch to preloaded cards if available
            } else {
                console.warn('No more cards available');
                document.getElementById('no-cards-message').classList.remove('hidden');
                return;
            }
        }

        cardData = mainCardsQueue[currentCardIndex];
        console.log('Current card:', cardData);

        // Handle case where the card has no content
        if (!cardData.card__side1) {
            console.warn('Empty card. Ending session.');
            document.getElementById('hidden-container').classList.add('hidden');
            document.getElementById('show-container-message').classList.remove('hidden');
            document.getElementById('show-container-trophy').classList.remove('hidden');
            return;
        }

        // Display the front side of the card or a play button for audio
        cardFront.innerText = studyFormat === 'audio' ? 'Play' : cardData.card__side1;

        // Reset UI elements for the new card
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

        // If we are close to the threshold, start loading more cards
        if (mainCardsQueue.length - currentCardIndex <= minCardsThreshold && preloadCardsQueue.length === 0) {
            console.log('Low on cards. Requesting more.');
            fetchCards();
        }
    }

    console.log('study_mode:', studyMode);

    // Function to show the 'Known' button based on card data and study mode
    function showKnownButton(cardData) {
        if (cardData) {
            knownButton.classList.add('hidden');
            if (!cardData.easiness && studyMode === 'new') {
                knownButton.classList.remove('hidden');
            }
        }
    }

    // Add event listeners for rating buttons
    document.querySelectorAll('.rating-button').forEach(button => {
        button.addEventListener('click', function () {
            const rating = parseInt(this.getAttribute('data-rating'));
            const cardData = mainCardsQueue[currentCardIndex];
            console.log(`Card rating: ${cardData.id}, Rating: ${rating}`);

            // Send rating to the server
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
                console.log('Rating submitted successfully');
            }).catch(error => console.error('Error submitting rating:', error));

            currentCardIndex++;
            loadCard();  // Load the next card
        });
    });

    // Load the first card
    loadCard();

    // Add event listener for showing the back side of the card
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

    // Add event listener for showing a hint for the current card
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

    // Add event listener for showing similar words related to the current card
    const showSimilarButton = document.getElementById('show-similar-btn');
    if (showSimilarButton) {
        showSimilarButton.addEventListener('click', function () {
            disableOtherActionButtons(this.id);
            const similarWordsUrl = config.urls.get_similar_words.replace('dummy_mappings_id', cardData.id);
            fetch(similarWordsUrl).then(response => response.json()).then(data => {
                similarWordsContainer.innerHTML = '';
                console.log('Similar words data:', data);

                data.similar_words.forEach(word => {
                    const button = document.createElement('button');
                    button.className = 'list-group-item list-group-item-action similar-words';
                    button.setAttribute('type', 'button');
                    button.innerText = word;

                    // Add click event to check if the selected word is correct
                    button.addEventListener('click', function () {
                        if (word === data.back_side) {
                            button.classList.add('correct-choice'); // Correct choice styling
                        } else {
                            button.classList.add('wrong-choice'); // Wrong choice styling
                            const correctButton = Array.from(similarWordsContainer.querySelectorAll('button')).find(btn => btn.innerText === data.back_side);
                            if (correctButton) {
                                correctButton.classList.add('correct-choice'); // Correct choice styling
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

    // Disable all similar word buttons after a selection is made
    function disableSimilarWordButtons() {
        const buttons = similarWordsContainer.querySelectorAll('button');
        buttons.forEach(button => {
            button.disabled = true;
        });
    }

    // Add event listener for showing the first letters of the answer
    const showFirstLettersButton = document.getElementById('show-first-letters-btn');
    if (showFirstLettersButton) {
        showFirstLettersButton.addEventListener('click', function () {
            disableOtherActionButtons(this.id);
            const sentence = cardData.card__side2;
            const words = sentence.split(' ');

            // Reveal letters incrementally based on the word count
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

    // Utility function to shuffle an array (used for scrambling letters)
    function shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
    }

    // Add event listeners for scrambling letters
    const scrambleLettersButton = document.getElementById('scramble-letters-btn');
    if (scrambleLettersButton) {
        scrambleLettersButton.addEventListener('click', function () {
            handleScrambleLettersClick();
        });
        scrambleLettersButton.addEventListener('touchstart', function () {
            handleScrambleLettersClick();
        });
    }

    // Function to handle the letter scrambling process
    function handleScrambleLettersClick() {
        disableOtherActionButtons(scrambleLettersButton.id);
        lettersContainer.innerHTML = '';
        const input = cardData.card__side2.trim();
        const words = input.split(' ');
        const isSentence = words.length > 2; // Check if it's a sentence (more than 2 words)
        let elements;

        // Split into words or letters based on input type
        if (isSentence) {
            elements = words.slice(); // Use a copy of the word array
        } else {
            elements = input.split(''); // Use letters for single words
        }

        shuffleArray(elements);
        let userInput = isSentence ? [] : ''; // Array for sentences, string for words

        // Create buttons for each element (letter/word) and add event listeners
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

                    // Apply changes immediately
                    span.classList.add('inactive');

                    // Delayed execution of the full match check and other actions
                    setTimeout(() => {
                        // Check if the user has fully reconstructed the word/sentence
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

            // Add event listeners for click and touchstart events
            span.addEventListener('click', handleClick);
            span.addEventListener('touchstart', handleClick);

            lettersContainer.appendChild(span);
        });
        lettersContainer.classList.remove('hidden');
    }

    // Disable all action buttons except the one that was just activated
    function disableOtherActionButtons(activeButtonId) {
        actionButtons.forEach(button => {
            if (button.id !== activeButtonId) {
                button.disabled = true;
            }
        });
    }

    // Make all action buttons inactive
    function makeButtonsInactive() {
        actionButtons.forEach(button => button.disabled = true);
    }

    // Event listener for playing the sound of the card front
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
