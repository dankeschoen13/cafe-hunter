const starInputs = document.querySelectorAll('.star-rating input[type="radio"]');

    starInputs.forEach(input => {
        input.addEventListener('change', function() {
            this.closest('form').submit();
        });
    });