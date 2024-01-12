function Source($filePath) {
    Get-Content $filePath | ForEach-Object { 
        if ($_ -match '^\s*[^#]') { 
            $key, $value = $_ -split '=', 2; 
            [System.Environment]::SetEnvironmentVariable($key, $value, [System.EnvironmentVariableTarget]::Process) 
        } 
    };
}


# Main

$help = @'
Usage: [command] [arguments]
Commands:
    'help'                  print this help
    'source' [path]         read env path
    'env' [filename]        load env file name from root project folder
    'm','manage.py' [args]  shorthand for 'python mobilidade_rio/manage.py [args]'
    'db', 'database','manage_db' [args]  run manage_db utility
    'runserver' [mode]      run server at modes
        mode:               'native'
'@

if ($args.Count -eq 0) {
    Write-Warning ("You must pass a command`n");
    Write-Host ($help);
    Exit;
}
    
elseif ($args[0] -eq "help") {
    Write-Host ($help);
    Exit;
}

elseif ($args[0] -eq "source") {
    if ($args.Count -lt 2) {
        Write-Warning ("You must pass argument");
        Write-Host ("Type './project help' for usage.");
        Exit;
    }
    Source($args[1]);
}

elseif ($args[0] -eq "env") {
    if ($args.Count -lt 2) {
        Write-Warning ("You must pass argument");
        Write-Host ("Type './project help' for usage.");
        Exit;
    }
    Source("mobilidade_rio/local_dev/" + $args[1] + ".env");
}

elseif ($($args[0] -eq "m") -or $($args[0] -eq "manage")) {
    python "mobilidade_rio/manage.py" $args[1..($args.Count)];
}

elseif ($($args[0] -eq "db") -or 
    $($args[0] -eq "database") -or $($args[0] -eq "manage_db")) {
    python "dev/scripts/manage_db/manage_db.py" $args[1..($args.Count)];
}

elseif ($args[0] -eq "runserver") {
    if ($args.Count -lt 2) {
        Write-Warning ("You must pass argument");
        Exit;
    }
    switch ($args[1]) {
        "native" { 
            python "mobilidade_rio/manage.py" migrate;
            python "mobilidade_rio/manage.py" runserver 8001;
         }
        Default {
            Write-Warning ("Invalid command");
            Write-Host ("Type './project help' for usage.");
        }
    }
}

else {
    Write-Warning ("Invalid command");
    Write-Host ("Type './project help' for usage.");
}