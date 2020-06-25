install_requirements() {
    ### Usage: install_requirements
    #
    #   This function will install the required packages from APT repository
    #   and Pypi repository. Those packages are all required for Re2o to work
    #   properly.
    ###

    echo "Setting up the required packages ..."
    pip3 install -r ../requirements.txt
    echo "Setting up the required packages: Done"
}


update_code(){
    ### Usage: update_code
    #
    #   This function will update the code of dinomail using git
    ###
    git pull
}

update_django() {
    ### Usage: update_django
    #
    #   This function will update the Django project by applying the migrations
    #   and collecting the statics
    ###

    echo "Applying Django migrations ..."
    python3 manage.py migrate
    echo "Applying Django migrations: Done"

    echo "Collecting web frontend statics ..."
    python3 manage.py collectstatic --noinput
    echo "Collecting web frontend statics: Done"

    echo "Generating locales ..."
    python3 manage.py compilemessages
    echo "Generating locales: Done"
}

main_function() {
    ### Usage: main_function [subcommand [options]]
    #
    #   This function will parse the arguments to determine which part of the tool to start.
    #   Refer to the help message below for the details of the parameters
    ###

    if [ -z "$1" ] || [ "$1" == "help" ]; then
        echo ""
        echo "Usage: install [subcommand [options]]"
        echo ""
        echo "The 'install' script is a utility script to setup, configure, reset and update"
        echo "some components of DinoMail. Please refer to the following details for more."
        echo ""
        echo "Sub-commands:"
        echo "  * [no subcommand] - Display this quick usage documentation"
        echo "  * {help} ---------- Display this quick usage documentation"
        echo "  * {setup} --------- Launch the full interactive guide to setup entirely"
        echo "                      re2o from scratch"
        echo "  * {update} -------- Collect frontend statics, install the missing APT"
        echo "                      and pip packages, copy LaTeX templates files"
	    echo "                      and apply the migrations to the DB"
        echo "  * {update-django} - Apply Django migration and collect frontend statics"
        echo "  * {update-packages} Install the missing APT and pip packages"
        echo "  * {update-settings} Interactively rewrite the settings file"
        echo ""
    else
        subcmd="$1"

        case "$subcmd" in

        setup )
           interactive_guide
           ;;

        update )
            update_code
            install_requirements
            update_django
            ;;

        update-django )
            update_django
            ;;

        update-packages )
            install_requirements
            ;;

        update-settings )
            interactive_update_settings
            ;;

        * )
            echo "Unknown subcommand: $subcmd"
            echo "Use 'install help' to display some help"
            ;;

        esac
    fi
}

main_function "$@"