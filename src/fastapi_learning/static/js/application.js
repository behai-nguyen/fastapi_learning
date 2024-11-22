/*
Date Created: 17/11/2024

Dependencies: https://github.com/behai-nguyen/js
*/

/*
Generic functions.
*/

function getWrittenListAfterSaved( status, tableName ) {
    if ( status == null ) return null;
    if ( !status.hasOwnProperty('data') ) return null;

    var key = tableName + '_new_list';
    if ( status.data.hasOwnProperty(key) && status.data[key].length > 0 )
        return status.data[ key ]
    else {
        key = tableName + '_updated_list';
        if ( status.data.hasOwnProperty(key) && status.data[key].length > 0 )
            return status.data[ key ];
    };

    return null;
}

function getErrorTextHtml( status ) {
    if ( status.data == undefined ) {
        return `<div>${status.status.text}</div>`;
    };
            
    let htmlMsgs = [];

    status.data.errors.forEach( ( err ) => {            
        htmlMsgs.push( '<span>' + err.label + '</span>' );
        htmlMsgs.push( '<ul>' );
        err.errors.forEach( (msg) => htmlMsgs.push('<li>'+ msg +'</li>') );
        htmlMsgs.push( '</ul>' );
    });

    return `<div>${htmlMsgs.join('')}</div>`;
}

/*
Employee pages' specific functions.
*/

function empEnableDisableButtons( state ) {
    $( '#saveEmpBtn' ).prop( 'disabled', state );
    $( '#newEmpBtn' ).prop( 'disabled', !state );
    $( '#empSearchBtn' ).prop( 'disabled', !state );
}

function empBindDataChange() {
    $( '.selector-input' ).on( 'change', function(event) {
        empEnableDisableButtons( false );
        setDataChanged();

        event.preventDefault();
    });
}

function saveEmployee( save_url ) {
    $( '#saveEmpBtn' ).on( 'click', ( event ) => {
        let data = $( '#empFrm' ).serialize();

        console.log(data);

        runAjaxCrossDomain( 'post', save_url, {},
                X_WWW_FORM_URLENCODED_UTF8, data ).
            then( function( response ) {
                let { status, textStatus, jqXHR } = response;

                if ( status.status.code != OK) {
                    displayError2( getErrorTextHtml(status) );
                }
                else {
                    var list = getWrittenListAfterSaved( status, 'employees' );
                    $( '#empNo' ).val( list[0].emp_no );
                    alert(status.status.text);

                    resetDataChanged();
                    empEnableDisableButtons( true );                        
                }
            }).
            catch( function( response ) {
                let { xhr, error, errorThrown } = response;

                alert( errorThrown );
            });

        event.preventDefault();
    })
}

function newEmployee() {
    $( '#newEmpBtn' ).on( 'click', ( event ) => {
        var url = $( event.target ).attr( 'data-url' );
        window.location.href = $( location ).attr( "origin" ) + '/' + url;

        event.preventDefault();
    })
}
