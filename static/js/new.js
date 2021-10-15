function hello() 
{
    alert('Good Evining Kishor')
}



$(document).ready(function()
{
    $(".blog_post").hover(function()
    {
        $(this).css("background-color", "orange");
    }, 
    function()
    {
        $(this).css("background-color", "white");
    });
});
