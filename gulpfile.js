'use strict';
// var pjson = require('./package.json');
var gulp = require('gulp');
var sass = require('gulp-sass');
// var gutil = require('gulp-util');
// var rename = require('gulp-rename');
// var uglify = require('gulp-uglify');
// var concat = require('gulp-concat');
 
gulp.task('scss', function () {
  return gulp.src('./flaskapp/static/scss/**/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('./flaskapp/static/css'));
});

gulp.task('default', ['scss']);
 
// gulp.task('default', function () {
//   gulp.watch('./static/scss/**/*.scss', ['scss']);
// });
