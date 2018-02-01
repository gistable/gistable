#!/usr/bin/env node

/**
 * Gistable CLI.
 *
 * Responsible for managing and unpacking gists as requested.
 */


// Core/NPM Modules
const _        = require('lodash');
const Bluebird = require('bluebird');
const fs       = require('fs');
const path     = require('path');
const spawn    = require('child_process').spawn;
const yargs    = require('yargs');


// Constants
const SOURCE_PATH = path.resolve(__dirname, 'dockerized-gists');
const DEST_PATH = process.cwd();


// Register clone command
yargs.command('clone <id> [dest]', 'Clone the gist directory', (yargs) => {

    yargs.positional('id', {
        describe: 'Gist ID',
        type: 'string'
    });
    yargs.positional('dest', {
        describe: 'Gist Destination',
        type: 'string'
    })

}, async (argv) => {

    try {

        // Get id and set final gist src and dest dirs
        let id = argv.id;
        let srcDir = path.join(SOURCE_PATH, id);
        let destDir = path.resolve(DEST_PATH, argv.dest || id);

        // Validate that the gist exists
        try {
            await Bluebird.fromCallback(cb => fs.access(srcDir, fs.constants.R_OK, cb));
        }
        catch (e) {
            throw new Error(`No such gist ${id}`);
        }

        // Validate that gisthub has write access to the destination path
        try {
            await Bluebird.fromCallback(cb => fs.access(DEST_PATH, fs.constants.W_OK, cb));
        }
        catch (e) {
            throw new Error(`No write access to ${DEST_PATH}`);
        }

        // Create gist directory
        await Bluebird.fromCallback(cb => fs.mkdir(destDir, cb));

        // Copy gist and dockerfile
        _.each(['snippet.py', 'Dockerfile'], async (file) => {

            await Bluebird.fromCallback(cb => fs.copyFile(
                path.join(srcDir, file),
                path.join(destDir, file),
                cb
            ));

        });


    }
    catch (e) {

        // Print error and exit
        console.error(e.toString());
        process.exit(1);

    }

});


// Register run command
yargs.command('run <id>', 'Build a docker image for a gist, then run it.', (yargs) => {

    yargs.positional('id', {
        describe: 'Gist ID',
        type: 'string'
    });

}, async (argv) => {

    // Try to build and run docker container
    try {

        // Get id and source directory
        let id = argv.id;
        let srcDir = path.join(SOURCE_PATH, id);

        // Validate that the gist exists
        try {
            await Bluebird.fromCallback(cb => fs.access(srcDir, fs.constants.R_OK, cb));
        }
        catch (e) {
            throw new Error(`No such gist ${id}`);
        }

        // Docker image name
        let image = `gistable/${id}`;

        // Build docker image
        spawn('docker', [
            'build',
            '-t',
            image,
            srcDir
        ], {
            stdio: 'inherit'
        }).on('close', (code) => {

            // Insert space in output for readability
            console.log();

            // If exit code was nonzero, error
            if (code) {
                console.error(`Docker build failed with exit code: ${code}`);
                process.exit(1);
            }

            // Run
            let run = spawn('docker', [
                'run',
                '--rm',
                '-it',
                image
            ], {
                stdio: 'inherit'
            }).on('close', (code) => {

                if (code) {
                    console.error(`Docker run failed with exit code: ${code}`);
                    process.exit(1);
                }

            });

        });

    }
    catch (e) {

        console.error(e.toString());
        process.exit(1);

    }

});


// Turn on help and access argv
yargs.help().argv;