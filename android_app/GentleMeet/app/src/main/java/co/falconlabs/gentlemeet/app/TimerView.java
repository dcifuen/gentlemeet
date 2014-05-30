package co.falconlabs.gentlemeet.app;

import android.content.Context;
import android.os.Handler;
import android.util.AttributeSet;
import android.view.View;
import android.widget.TextView;

import com.google.api.client.util.DateTime;

import org.joda.time.Period;

import java.util.Date;

/**
 * Created by jorgesalcedo on 5/30/14.
 */
public class TimerView extends TextView {
    private static final String TEMPLATE = "%s";
    private DateTime endDate;

    Handler handler = new Handler();
    Runnable runnable = new Runnable() {
        public void run() {
            updateTimer();
        }
    };

    public TimerView(Context context, AttributeSet attrs){
        super(context, attrs);
    }
    public void setEndTime(DateTime date) {
        endDate = date;
        updateTimer();
    }

    private String getTimerText(DateTime date){
        Period period = new Period((new Date()).getTime(), date.getValue());
        String hourText = String.format("%02d", period.getHours());
        String minuteText = String.format("%02d", period.getMinutes());
        String secondsText = String.format("%02d", period.getSeconds());
        String durationText = hourText+":"+minuteText+":"+secondsText;
        return durationText;
    }
    private void updateTimer(){
        setText(getTimerText(endDate));
        handler.postDelayed(runnable, 1000);
    }

}
