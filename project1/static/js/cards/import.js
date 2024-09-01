document.addEventListener('DOMContentLoaded', function () {
    // Variables to hold references to important DOM elements
    var customOptionInput1 = document.getElementById('id_words_separator_custom');
    var customOptionInput2 = document.getElementById('id_cards_separator_custom');
    var customRadio1 = document.getElementById('id_words_separator_2');
    var customRadio2 = document.getElementById('id_cards_separator_2');
    var textInput = document.getElementById('id_text');
    var previewContainer = document.getElementById('preview');
    var previewContainerWrapper = document.getElementById('preview-container');
    var cardCountElement = document.getElementById('card-count');

    // Insert a tab character in the text input when the Tab key is pressed
    textInput.addEventListener('keydown', function (e) {
        if (e.key === 'Tab') {
            e.preventDefault();
            var start = this.selectionStart;
            var end = this.selectionEnd;
            this.value = this.value.substring(0, start) + '\t' + this.value.substring(end);
            this.selectionStart = this.selectionEnd = start + 1;
            updatePreview(); // Update the preview after inserting the tab
        }
    });

    // Function to escape HTML special characters to prevent XSS attacks
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

    // Function to update the preview of the cards based on the input text and separators
    function updatePreview() {
        var text = textInput.value;
        var wordsSeparator = document.querySelector('input[name="words_separator"]:checked').value;
        var cardsSeparator = document.querySelector('input[name="cards_separator"]:checked').value;
        var wordsSeparatorCustom = customOptionInput1.value;
        var cardsSeparatorCustom = customOptionInput2.value;

        // Show or hide the preview container based on whether there's any text
        if (!text.trim()) {
            previewContainerWrapper.style.display = 'none';
            cardCountElement.textContent = 'Cards: 0';
            return;
        } else {
            previewContainerWrapper.style.display = 'block';
        }

        // Determine the separators to use based on the selected options
        var wordsSeparatorValue = (wordsSeparator === 'words_custom' && wordsSeparatorCustom) ? wordsSeparatorCustom : (wordsSeparator === 'tab' ? '\t' : (wordsSeparator === 'comma' ? ',' : null));
        var cardsSeparatorValue = (cardsSeparator === 'cards_custom' && cardsSeparatorCustom) ? cardsSeparatorCustom : (cardsSeparator === 'new_line' ? '\n' : (cardsSeparator === 'semicolon' ? ';' : null));

        // Check if custom separators are required but not provided
        if ((wordsSeparator === 'words_custom' && !wordsSeparatorCustom) || (cardsSeparator === 'cards_custom' && !cardsSeparatorCustom)) {
            previewContainer.textContent = "Please enter custom separators.";
            return;
        }

        // Split the text into cards and words using the determined separators
        var cards = text.split(cardsSeparatorValue).filter(card => card.trim() !== '');
        previewContainer.innerHTML = ''; // Clear the preview container before adding new cards

        // Generate preview for each card
        cards.forEach(card => {
            var cardElement = document.createElement('div');
            cardElement.className = 'card';

            var words = card.split(wordsSeparatorValue);
            var formattedText = words.map(word => escapeHTML(word.trim())).join('<br>');

            cardElement.innerHTML = formattedText;
            previewContainer.appendChild(cardElement);
        });

        // Update the card count display
        cardCountElement.textContent = 'Cards: ' + cards.length;
    }

    // Automatically select the custom radio button when a custom input field is focused
    customOptionInput1.addEventListener('focus', function () {
        customRadio1.checked = true;
    });

    customOptionInput2.addEventListener('focus', function () {
        customRadio2.checked = true;
    });

    // Add event listeners to update the preview when the text or separators change
    textInput.addEventListener('input', updatePreview);
    document.querySelectorAll('input[name="words_separator"]').forEach(function (radio) {
        radio.addEventListener('change', updatePreview);
    });
    document.querySelectorAll('input[name="cards_separator"]').forEach(function (radio) {
        radio.addEventListener('change', updatePreview);
    });
    customOptionInput1.addEventListener('input', updatePreview);
    customOptionInput2.addEventListener('input', updatePreview);

    // Initialize the preview when the page loads
    updatePreview();
});
