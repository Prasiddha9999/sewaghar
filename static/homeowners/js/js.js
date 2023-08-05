window.onload = function() {
    // Get the search bar and services list
 const searchBar = document.getElementById('searchBar');
 const servicesList = document.querySelector('.row');

 // Add event listener to search bar
 searchBar.addEventListener('input', () => {
  
   // Get the search query
   const query = searchBar.value.toLowerCase();

   // Filter the services list
   const filteredServices = Array.from(servicesList.children).filter(service => {
     const serviceName = service.querySelector('.card-title').textContent.toLowerCase();
     return serviceName.includes(query);
   });

   // Hide/show services based on the filter
   Array.from(servicesList.children).forEach(service => {
     if (filteredServices.includes(service)) {
       service.style.display = 'block';
     } else {
       service.style.display = 'none';
     }
   });
 });

 // Function to clear the search bar and show all services
 function searchServices() {
   searchBar.value = '';
   Array.from(servicesList.children).forEach(service => {
     service.style.display = 'block';
   });
 }

 //for filter service by loaction
 const searchInput = document.getElementById('location-search');
 searchInput.addEventListener('input', filterByLocation);
 function filterByLocation() {
    const searchQuery = searchInput.value.trim().toLowerCase();
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
      const location = row.querySelector('td:nth-child(3)').textContent.trim().toLowerCase();
      if (location.includes(searchQuery)) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  }
  

 };


