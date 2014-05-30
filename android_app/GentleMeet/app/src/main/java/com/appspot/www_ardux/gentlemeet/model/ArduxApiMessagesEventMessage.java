/*
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
 * in compliance with the License. You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License
 * is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
 * or implied. See the License for the specific language governing permissions and limitations under
 * the License.
 */
/*
 * This code was generated by https://code.google.com/p/google-apis-client-generator/
 * (build: 2014-04-15 19:10:39 UTC)
 * on 2014-05-30 at 04:19:15 UTC 
 * Modify at your own risk.
 */

package com.appspot.www_ardux.gentlemeet.model;

/**
 * Model definition for ArduxApiMessagesEventMessage.
 *
 * <p> This is the Java data model class that specifies how to parse/serialize into the JSON that is
 * transmitted over HTTP when working with the GentleMeet API. For a detailed explanation see:
 * <a href="http://code.google.com/p/google-http-java-client/wiki/JSON">http://code.google.com/p/google-http-java-client/wiki/JSON</a>
 * </p>
 *
 * @author Google, Inc.
 */
@SuppressWarnings("javadoc")
public final class ArduxApiMessagesEventMessage extends com.google.api.client.json.GenericJson {

  /**
   * The value may be {@code null}.
   */
  @com.google.api.client.util.Key("actual_attendees")
  private java.util.List<java.lang.String> actualAttendees;

  /**
   * The value may be {@code null}.
   */
  @com.google.api.client.util.Key
  private java.lang.String description;

  /**
   * The value may be {@code null}.
   */
  @com.google.api.client.util.Key("end_date_time")
  private com.google.api.client.util.DateTime endDateTime;

  /**
   * The value may be {@code null}.
   */
  @com.google.api.client.util.Key
  private java.lang.String id;

  /**
   * The value may be {@code null}.
   */
  @com.google.api.client.util.Key("maybe_attendees")
  private java.util.List<java.lang.String> maybeAttendees;

  /**
   * The value may be {@code null}.
   */
  @com.google.api.client.util.Key("no_attendees")
  private java.util.List<java.lang.String> noAttendees;

  /**
   * The value may be {@code null}.
   */
  @com.google.api.client.util.Key("no_response_attendees")
  private java.util.List<java.lang.String> noResponseAttendees;

  /**
   * The value may be {@code null}.
   */
  @com.google.api.client.util.Key
  private java.lang.String organizer;

  /**
   * The value may be {@code null}.
   */
  @com.google.api.client.util.Key("remaining_time") @com.google.api.client.json.JsonString
  private java.lang.Long remainingTime;

  /**
   * The value may be {@code null}.
   */
  @com.google.api.client.util.Key("start_date_time")
  private com.google.api.client.util.DateTime startDateTime;

  /**
   * The value may be {@code null}.
   */
  @com.google.api.client.util.Key
  private java.lang.String state;

  /**
   * The value may be {@code null}.
   */
  @com.google.api.client.util.Key
  private java.lang.String summary;

  /**
   * The value may be {@code null}.
   */
  @com.google.api.client.util.Key
  private java.lang.String title;

  /**
   * The value may be {@code null}.
   */
  @com.google.api.client.util.Key("yes_attendees")
  private java.util.List<java.lang.String> yesAttendees;

  /**
   * @return value or {@code null} for none
   */
  public java.util.List<java.lang.String> getActualAttendees() {
    return actualAttendees;
  }

  /**
   * @param actualAttendees actualAttendees or {@code null} for none
   */
  public ArduxApiMessagesEventMessage setActualAttendees(java.util.List<java.lang.String> actualAttendees) {
    this.actualAttendees = actualAttendees;
    return this;
  }

  /**
   * @return value or {@code null} for none
   */
  public java.lang.String getDescription() {
    return description;
  }

  /**
   * @param description description or {@code null} for none
   */
  public ArduxApiMessagesEventMessage setDescription(java.lang.String description) {
    this.description = description;
    return this;
  }

  /**
   * @return value or {@code null} for none
   */
  public com.google.api.client.util.DateTime getEndDateTime() {
    return endDateTime;
  }

  /**
   * @param endDateTime endDateTime or {@code null} for none
   */
  public ArduxApiMessagesEventMessage setEndDateTime(com.google.api.client.util.DateTime endDateTime) {
    this.endDateTime = endDateTime;
    return this;
  }

  /**
   * @return value or {@code null} for none
   */
  public java.lang.String getId() {
    return id;
  }

  /**
   * @param id id or {@code null} for none
   */
  public ArduxApiMessagesEventMessage setId(java.lang.String id) {
    this.id = id;
    return this;
  }

  /**
   * @return value or {@code null} for none
   */
  public java.util.List<java.lang.String> getMaybeAttendees() {
    return maybeAttendees;
  }

  /**
   * @param maybeAttendees maybeAttendees or {@code null} for none
   */
  public ArduxApiMessagesEventMessage setMaybeAttendees(java.util.List<java.lang.String> maybeAttendees) {
    this.maybeAttendees = maybeAttendees;
    return this;
  }

  /**
   * @return value or {@code null} for none
   */
  public java.util.List<java.lang.String> getNoAttendees() {
    return noAttendees;
  }

  /**
   * @param noAttendees noAttendees or {@code null} for none
   */
  public ArduxApiMessagesEventMessage setNoAttendees(java.util.List<java.lang.String> noAttendees) {
    this.noAttendees = noAttendees;
    return this;
  }

  /**
   * @return value or {@code null} for none
   */
  public java.util.List<java.lang.String> getNoResponseAttendees() {
    return noResponseAttendees;
  }

  /**
   * @param noResponseAttendees noResponseAttendees or {@code null} for none
   */
  public ArduxApiMessagesEventMessage setNoResponseAttendees(java.util.List<java.lang.String> noResponseAttendees) {
    this.noResponseAttendees = noResponseAttendees;
    return this;
  }

  /**
   * @return value or {@code null} for none
   */
  public java.lang.String getOrganizer() {
    return organizer;
  }

  /**
   * @param organizer organizer or {@code null} for none
   */
  public ArduxApiMessagesEventMessage setOrganizer(java.lang.String organizer) {
    this.organizer = organizer;
    return this;
  }

  /**
   * @return value or {@code null} for none
   */
  public java.lang.Long getRemainingTime() {
    return remainingTime;
  }

  /**
   * @param remainingTime remainingTime or {@code null} for none
   */
  public ArduxApiMessagesEventMessage setRemainingTime(java.lang.Long remainingTime) {
    this.remainingTime = remainingTime;
    return this;
  }

  /**
   * @return value or {@code null} for none
   */
  public com.google.api.client.util.DateTime getStartDateTime() {
    return startDateTime;
  }

  /**
   * @param startDateTime startDateTime or {@code null} for none
   */
  public ArduxApiMessagesEventMessage setStartDateTime(com.google.api.client.util.DateTime startDateTime) {
    this.startDateTime = startDateTime;
    return this;
  }

  /**
   * @return value or {@code null} for none
   */
  public java.lang.String getState() {
    return state;
  }

  /**
   * @param state state or {@code null} for none
   */
  public ArduxApiMessagesEventMessage setState(java.lang.String state) {
    this.state = state;
    return this;
  }

  /**
   * @return value or {@code null} for none
   */
  public java.lang.String getSummary() {
    return summary;
  }

  /**
   * @param summary summary or {@code null} for none
   */
  public ArduxApiMessagesEventMessage setSummary(java.lang.String summary) {
    this.summary = summary;
    return this;
  }

  /**
   * @return value or {@code null} for none
   */
  public java.lang.String getTitle() {
    return title;
  }

  /**
   * @param title title or {@code null} for none
   */
  public ArduxApiMessagesEventMessage setTitle(java.lang.String title) {
    this.title = title;
    return this;
  }

  /**
   * @return value or {@code null} for none
   */
  public java.util.List<java.lang.String> getYesAttendees() {
    return yesAttendees;
  }

  /**
   * @param yesAttendees yesAttendees or {@code null} for none
   */
  public ArduxApiMessagesEventMessage setYesAttendees(java.util.List<java.lang.String> yesAttendees) {
    this.yesAttendees = yesAttendees;
    return this;
  }

  @Override
  public ArduxApiMessagesEventMessage set(String fieldName, Object value) {
    return (ArduxApiMessagesEventMessage) super.set(fieldName, value);
  }

  @Override
  public ArduxApiMessagesEventMessage clone() {
    return (ArduxApiMessagesEventMessage) super.clone();
  }

}
