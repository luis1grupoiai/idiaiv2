const gulp = require('gulp');

// Tarea para copiar archivos JS
gulp.task('copy-js', function() {
    return gulp.src('node_modules/toastify-js/src/toastify.js')
        .pipe(gulp.dest('staticfiles/js/'));
});

// Tarea para copiar archivos CSS
gulp.task('copy-css', function() {
    return gulp.src('node_modules/toastify-js/src/*.css')
        .pipe(gulp.dest('staticfiles/css/'));
});

// Tarea por defecto que ejecuta ambas tareas
gulp.task('default', gulp.parallel('copy-js', 'copy-css'));
