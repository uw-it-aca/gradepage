// Adds a helper for django's i18n js api
Handlebars.registerHelper("trans", function() {
    switch(arguments.length) {
        case 1:
            // No text to translate
            return no_trans_key(arguments[0]);
        case 2:
            // A single translation key
            return single(arguments[0], this);
        case 3:
            // An invalid plural - treat it like it's single
            return single(arguments[0], this);
        case 4:
            // Proper plural
            return plural(arguments[0], arguments[1], arguments[2], this);
        default:
            // Something else - just return something empty.
            return no_trans_key({});
    }

    function no_trans_key() {
        return "";
    }

    function single(key, obj) {
        if (undefined === key) {
            console.log("Undefined value for trans - is your msgid in quotes?");
            return "";
        }
        var base = gettext(key);
        return interpolate(base, obj, true);
    }

    function plural(key1, key2, count, obj) {
        if (undefined === key1 || undefined === key2) {
            console.log("Undefined value for trans - is your msgid in quotes?");
            return "";
        }
        var base = ngettext(key1, key2, count);
        return interpolate(base, obj, true);
    }

});
