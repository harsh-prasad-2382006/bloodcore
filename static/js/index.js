const toggleButton = document.getElementById('navbarToggle');
  const navbarCollapse = document.getElementById('navbarContent');
  
  navbarCollapse.addEventListener('show.bs.collapse', function () {
    toggleButton.innerHTML = '<span style="font-size:1.8rem;">&times;</span>'; // × Cross
  });

  navbarCollapse.addEventListener('hide.bs.collapse', function () {
    toggleButton.innerHTML = '<span class="navbar-toggler-icon"></span>'; // Hamburger
  });

  

  function fetchAddress() {
    const pincode = document.getElementById("pincode").value;
    
    // Reset fields if pincode is empty or incorrect length
    if (pincode.length !== 6) {
        document.getElementById("state").value = "";
        document.getElementById("city").value = "";
        document.getElementById("taluka").value = "";
        return;
    }

    // Fetch address details based on pincode
    fetch(`https://api.postalpincode.in/pincode/${pincode}`)
        .then(response => response.json())
        .then(data => {
            if (data[0].Status === "Success") {
                const info = data[0].PostOffice[0];
                // Populate fields with the fetched data
                document.getElementById("state").value = info.State || "";
                document.getElementById("city").value = info.District || "";
                document.getElementById("taluka").value = info.Taluk || info.Block || info.Name || "";
            } else {
                alert("Invalid pincode. Please enter a valid 6-digit pincode.");
                // Clear fields in case of invalid pincode
                document.getElementById("state").value = "";
                document.getElementById("city").value = "";
                document.getElementById("taluka").value = "";
            }
        })
        .catch(error => {
            alert("Error fetching address details.");
            console.error("API Error:", error);
        });
}


