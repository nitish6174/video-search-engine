'use strict';
var pjson = require('./package.json');
var gulp = require('gulp');
var sass = require('gulp-sass');
// var gutil = require('gulp-util');
// var rename = require('gulp-rename');
// var uglify = require('gulp-uglify');
// var concat = require('gulp-concat');
 
gulp.task('scss', function () {
  return gulp.src('./static/scss/**/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('./static/css'));
});
 
gulp.task('sass:watch', function () {
  gulp.watch('./static/scss/**/*.scss', ['scss']);
});
