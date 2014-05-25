package co.falconlabs.gentlemeet.app;

import android.accounts.Account;
import android.accounts.AccountManager;
import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Toast;

import com.google.android.gms.auth.GoogleAuthException;
import com.google.android.gms.auth.GoogleAuthUtil;
import com.google.android.gms.common.AccountPicker;
import com.google.api.client.googleapis.extensions.android.gms.auth.GoogleAccountCredential;

import java.io.IOException;


public class SigninActivity extends Activity{

    private static final String LOG_TAG = SigninActivity.class.getName();

    /* Request code used to invoke sign in user interactions. */
    private static final int RC_SIGN_IN = 0;

    /* Client used to interact with Google APIs. */

    /* A flag indicating that a PendingIntent is in progress and prevents
     * us from starting further intents.
     */
    private boolean mIntentInProgress;

    private static final int ACTIVITY_RESULT_FROM_ACCOUNT_SELECTION = 2222;

    private AuthorizationCheckTask mAuthTask;

    String mEmailAccount;

    SharedPreferences prefs;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_signin);
        getActionBar().setTitle(R.string.signin);
        prefs = PreferenceManager.getDefaultSharedPreferences(this);
        mEmailAccount = prefs.getString("pref_email", "");
    }

    protected void onStart() {
        super.onStart();
    }

    protected void onStop() {
        super.onStop();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (mAuthTask!=null) {
            mAuthTask.cancel(true);
            mAuthTask = null;
        }
    }

    public void onClickSignIn(View view) {
        // Check to see how many Google accounts are registered with the device.
        // No accounts registered, nothing to do.
        int googleAccounts = AppConstants.countGoogleAccounts(this);
        if (googleAccounts == 0) {
            // No accounts registered, nothing to do.
            Toast.makeText(this, R.string.toast_no_google_accounts_registered,
                    Toast.LENGTH_LONG).show();
        } else if (googleAccounts == 1) {
            AccountManager am = AccountManager.get(this);
            Account[] accounts = am.getAccountsByType(GoogleAuthUtil.GOOGLE_ACCOUNT_TYPE);
            if (accounts != null && accounts.length > 0) {
                mEmailAccount = accounts[0].name;
                SharedPreferences.Editor editor = prefs.edit();
                editor.putString("pref_email", mEmailAccount);
                editor.commit();
                performAuthCheck(accounts[0].name);
            }
        } else {
            // More than one Google Account is present, a chooser is necessary.
            // Invoke an {@code Intent} to allow the user to select a Google account.
            Intent accountSelector = AccountPicker.newChooseAccountIntent(null, null,
                    new String[]{GoogleAuthUtil.GOOGLE_ACCOUNT_TYPE}, false,
                    "Select the account to access GentleMeet.", null, null, null);
            startActivityForResult(accountSelector,
                    ACTIVITY_RESULT_FROM_ACCOUNT_SELECTION);
        }

    }

    protected void onActivityResult(int requestCode, int responseCode, Intent intent) {
        super.onActivityResult(requestCode, responseCode, intent);

        if (requestCode == ACTIVITY_RESULT_FROM_ACCOUNT_SELECTION && responseCode == RESULT_OK) {
            // This path indicates the account selection activity resulted in the user selecting a
            // Google account and clicking OK.

            // Set the selected account.
            String accountName = intent.getStringExtra(AccountManager.KEY_ACCOUNT_NAME);
            mEmailAccount = accountName;
            SharedPreferences.Editor editor = prefs.edit();
            editor.putString("pref_email", mEmailAccount);
            editor.commit();
            performAuthCheck(accountName);
        }
    }

    public void performAuthCheck(String emailAccount) {
        // Cancel previously running tasks.
        if (mAuthTask != null) {
            try {
                mAuthTask.cancel(true);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        new AuthorizationCheckTask().execute(emailAccount);
    }

    class AuthorizationCheckTask extends AsyncTask<String, Integer, Boolean> {
        @Override
        protected Boolean doInBackground(String... emailAccounts) {
            Log.i(LOG_TAG, "Background task started.");

            if (!AppConstants.checkGooglePlayServicesAvailable(SigninActivity.this)) {
                return false;
            }

            String emailAccount = emailAccounts[0];
            // Ensure only one task is running at a time.
            mAuthTask = this;

            Log.d(LOG_TAG, "Attempting to get AuthToken for account: " + mEmailAccount);

            try {
                // If the application has the appropriate access then a token will be retrieved, otherwise
                // an error will be thrown.
                GoogleAccountCredential credential = GoogleAccountCredential.usingAudience(
                        SigninActivity.this, AppConstants.AUDIENCE);

                credential.setSelectedAccountName(emailAccount);

                String accessToken = credential.getToken();

                Log.d(LOG_TAG, "AccessToken retrieved");

                // Success.
                return true;
            } catch (GoogleAuthException unrecoverableException) {
                Log.e(LOG_TAG, "Exception checking OAuth2 authentication.", unrecoverableException);
                publishProgress(R.string.toast_exception_checking_authorization);
                // Failure.
                return false;
            } catch (IOException ioException) {
                Log.e(LOG_TAG, "Exception checking OAuth2 authentication.", ioException);
                publishProgress(R.string.toast_exception_checking_authorization);
                // Failure or cancel request.
                return false;
            }
        }

        @Override
        protected void onProgressUpdate(Integer... stringIds) {
            // Toast only the most recent.
            Integer stringId = stringIds[0];
            Toast.makeText(SigninActivity.this, stringId, Toast.LENGTH_SHORT).show();
        }

        @Override
        protected void onPreExecute() {
            mAuthTask = this;
        }

        @Override
        protected void onPostExecute(Boolean success) {
            if (success) {
                Intent intent = new Intent(SigninActivity.this, MainActivity.class);
                startActivity(intent);
                finish();
            } else {
                Intent intent = new Intent(SigninActivity.this, SigninActivity.class);
                startActivity(intent);
                finish();
            }
            mAuthTask = null;
        }

        @Override
        protected void onCancelled() {
            mAuthTask = null;
        }
    }
}
