package co.falconlabs.gentlemeet.app;

/**
 * Created by jorgesalcedo on 2/9/14.
 */
import com.appspot.www_ardux.gentlemeet.model.ResourceCalendar;
import com.google.api.client.util.Lists;

import java.util.ArrayList;

/**
 * Dummy Application class that can hold static data for use only in sample applications.
 *
 * TODO(developer): Implement a proper data storage technique for your application.
 */
public class Application extends android.app.Application {
    ArrayList<ResourceCalendar> rooms = Lists.newArrayList();
}
