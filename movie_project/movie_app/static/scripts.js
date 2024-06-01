// 假设有一个包含电影信息的JavaScript对象
var movieData = {
    moviename: "Movie Name",
    length: 120,
    releaseyear: 2022,
    plot_summary: "This is a plot summary",
    resource_link: "http://example.com",
    production_company_id: 1
};

// 使用fetch API发送POST请求
fetch('/add_movie/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(movieData),
})
.then(response => {
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    return response.json();
})
.then(data => {
    console.log(data);
})
.catch(error => {
    console.error('There was a problem with the POST request:', error);
});
