document.addEventListener('DOMContentLoaded',function(){
    const dashboardLink=document.getElementByID('dashboardLink');
    dashboardLink.addEventListener ('click',function(event){
        event.preventDefault();
        window.location.href='user-details.html';
    });
} );     