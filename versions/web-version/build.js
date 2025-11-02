#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Simple TypeScript to JavaScript transpiler for basic ES6 modules
function transpileFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    
    // Remove TypeScript type annotations (basic regex)
    let jsContent = content
        .replace(/:\s*[A-Za-z0-9\[\]|&\s]+(\s*=\s*[^,;\)]+)?/g, (match, defaultValue) => {
            return defaultValue || '';
        })
        .replace(/as\s+const/g, '')
        .replace(/readonly\s+/g, '')
        .replace(/export\s+type\s+[^;]+;/g, '')
        .replace(/export\s+interface\s+[^{]+\{[^}]*\}/g, '')
        .replace(/abstract\s+/g, '')
        .replace(/protected\s+/g, '')
        .replace(/private\s+/g, '')
        .replace(/public\s+/g, '')
        .replace(/get\s+(\w+)\(\)\s*:\s*[^{]+/g, 'get $1()')
        .replace(/set\s+(\w+)\([^)]+\)\s*:\s*void/g, 'set $1(value)')
        .replace(/\/\*\*[\s\S]*?\*\//g, '') // Remove JSDoc comments
        .replace(/\/\/.*$/gm, ''); // Remove single line comments
    
    return jsContent;
}

function buildProject() {
    const srcDir = 'src';
    const distDir = 'dist';
    
    // Create dist directory
    if (!fs.existsSync(distDir)) {
        fs.mkdirSync(distDir, { recursive: true });
    }
    
    // Recursively process all TypeScript files
    function processDirectory(dir, relativePath = '') {
        const items = fs.readdirSync(dir);
        
        for (const item of items) {
            const fullPath = path.join(dir, item);
            const relativeItemPath = path.join(relativePath, item);
            const stat = fs.statSync(fullPath);
            
            if (stat.isDirectory()) {
                // Create subdirectory in dist
                const distSubDir = path.join(distDir, relativeItemPath);
                if (!fs.existsSync(distSubDir)) {
                    fs.mkdirSync(distSubDir, { recursive: true });
                }
                processDirectory(fullPath, relativeItemPath);
            } else if (item.endsWith('.ts')) {
                // Transpile TypeScript file
                const jsContent = transpileFile(fullPath);
                const jsFileName = item.replace('.ts', '.js');
                const distPath = path.join(distDir, relativeItemPath.replace('.ts', '.js'));
                fs.writeFileSync(distPath, jsContent);
                console.log(`Transpiled: ${fullPath} -> ${distPath}`);
            }
        }
    }
    
    processDirectory(srcDir);
    console.log('Build completed!');
}

buildProject();
