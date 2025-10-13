$(document).ready(function() {
  // 從伺服器獲取並顯示已存在的圖片
  loadExistingImages();

  function handleFormSubmit(event, selector) {
      event.preventDefault();
      event.stopPropagation();
      const files = event.originalEvent.dataTransfer ? event.originalEvent.dataTransfer.files : event.target.files;
      const formId = $(this).parents('form').attr('id');
      const formData = new FormData($('#' + formId)[0]);
      formData.append('fileToUpload', files[0]);  // 使用 'fileToUpload' 代替 'image'

      // Submit the form using AJAX
      $.ajax({
          url: '/upload',
          type: 'POST',
          data: formData,
          processData: false,
          contentType: false,
          success: function(response) {
              console.log(`Upload successful for ${selector}:`, response);
          },
          error: function(xhr, status, error) {
              console.log(`Upload failed for ${selector}:`, error);
          }
      });
  }

  // Bind events for multiple selectors
  const uploadSelectors = ['1', '2'];
  uploadSelectors.forEach(selector => {
      $(`.upload-button__input${selector}`).on('change', function(event) {
          handleFormSubmit.call(this, event, selector);
      });
      $(`.upload-button${selector}`).on('dragover dragenter', function(e) {
          e.preventDefault();
          e.stopPropagation();
      }).on('drop', function(event) {
          handleFormSubmit.call(this, event, selector);
      });
  });

  // Image preview for uploaded files
  const mappings = {
      'upload-button__input1': 'mytop',
      'upload-button__input2': 'mybutton'
  };

  Object.keys(mappings).forEach(inputClass => {
      document.querySelector(`.${inputClass}`).addEventListener('change', function(e) {
          handleFileUpload(e, document.getElementById(mappings[inputClass]));
      });
  });

  function handleFileUpload(e, targetElement) {
      const file = e.target.files[0];
      if (file) {
          const imageURL = URL.createObjectURL(file);
          const newImage = document.createElement('img');
          newImage.src = imageURL;
          newImage.id = 'Diffusion';
          newImage.classList.add('uploaded-image');
          targetElement.insertBefore(newImage, targetElement.firstChild);
      }
  }
});

// Function to fetch and display existing images from the server in reverse order
function loadExistingImages() {
    $.ajax({
      url: '',
      type: 'GET',
      success: function(images) {
        // Assuming `images` is an array of image URLs
        images.reverse(); // Reverse the array to display in reverse order
        images.forEach(function(imageURL) {
          const newImage = document.createElement('img');
          newImage.src = imageURL;
          newImage.classList.add('uploaded-image');
          document.body.appendChild(newImage);  // Adjust this as per your specific placement needs
        });
      },
      error: function(xhr, status, error) {
        console.log('Error fetching images:', error);
      }
    });


        // 点击mytop中的图像后显示在leftT
    $('#mytop img').on('click', function() {
        const imageURL = $(this).attr('src');
        $('#selectTop').attr('src', imageURL);
    });

    // 点击mybutton中的图像后显示在leftB
    $('#mybutton img').on('click', function() {
        const imageURL = $(this).attr('src');
        $('#selectBottom').attr('src', imageURL);
    });


    

    $('#generate-button').on('click', function() {
        const topImageURL = $('#selectTop').attr('src');
        const bottomImageURL = $('#selectBottom').attr('src');
    
        $.ajax({
            url: '/getPrompt',
            method: 'POST',
            data: {topImageURL: topImageURL, bottomImageURL: bottomImageURL},
            success: function(response) {
                if (response.success) {
                    window.location.href = response.redirect_url;
                } else {
                    console.log('Error:', response.error);
                }
            },
            error: function(error) {
                console.log('Error:', error);
            }
        });
    });
    

    
  }

    