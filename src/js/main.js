// Load all CSS files in the src directory
import.meta.glob('../css/vendor/*.css', {
    eager: true,
})
import.meta.glob('../css/*.css', {
    eager: true,
})

// Load all JavaScript files in the current directory
import.meta.glob('./vendor/*.js', {
    eager: true,
})
import.meta.glob('./*.js', {
    eager: true,
})

//import 'htmx.org'
